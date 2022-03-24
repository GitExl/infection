from operator import itemgetter
from typing import Dict

from wadassembler.context import Context
from wadassembler.namespaces import namespaces


class Assembler:

    def __init__(self, context: Context):
        self.context: Context = context

    def assemble(self):

        # Read and process namespaces.
        for namespace_name, namespace_info in namespaces.items():
            print('Reading {}...'.format(namespace_name))

            if namespace_name not in self.context.namespaces:
                self.context.namespaces[namespace_name] = {}

            for pattern, funcs in namespace_info['patterns'].items():
                for file_path in self.context.source_path.glob(pattern):

                    # Read resource.
                    read_func = funcs[0]
                    resources = read_func(self.context, file_path)

                    if resources is None:
                        continue

                    # Run process functions.
                    for name, resource in resources:
                        for process_func in funcs[1:]:
                            resource = process_func(self.context, namespace_name, name, resource)
                            if resource is None:
                                break

                        if resource is not None:
                            self.context.namespaces[namespace_name][name] = resource

        # Run filter functions.
        for namespace_name, namespace_info in reversed(namespaces.items()):
            if 'filter' not in namespace_info:
                continue

            print('Filtering {}...'.format(namespace_name))
            self.context.namespaces[namespace_name] = namespace_info['filter'](self.context, self.context.namespaces[namespace_name])

        # Sort by name.
        for namespace_name, namespace_info in reversed(namespaces.items()):
            self.context.namespaces[namespace_name] = dict(sorted(self.context.namespaces[namespace_name].items()))

        # Write types by namespace.
        for namespace_name, namespace_info in namespaces.items():
            if namespace_name in self.context.config['disabled_namespace_writing']:
                continue

            print('Writing {}...'.format(namespace_name))

            if 'markers' in namespace_info:
                marker_start = namespace_info['markers'][0]
                self.context.wad.add_lump(marker_start, bytes())

            namespace_info['writer'](self.context, self.context.namespaces[namespace_name])

            if 'markers' in namespace_info:
                marker_end = namespace_info['markers'][1]
                self.context.wad.add_lump(marker_end, bytes())

        print('Writing WAD index...')
        self.context.wad.write()

        self.write_usage_reports(self.context)

    def write_usage_reports(self, context: Context):
        if 'usage_report_textures' in context.config:
            print('Writing texture usage report...')

            with open(context.config['usage_report_textures'], 'w') as f:
                for name, count in self.create_usage_dict(context.used_textures).items():
                    f.write('"{}",{}\n'.format(name, count))

        if 'usage_report_flats' in context.config:
            print('Writing flat usage report...')

            with open(context.config['usage_report_flats'], 'w') as f:
                for name, count in self.create_usage_dict(context.used_flats).items():
                    f.write('"{}",{}\n'.format(name, count))

    def create_usage_dict(self, items: Dict[str, int]) -> Dict[str, int]:
        normalized_items = {}

        for name, count in sorted(items.items()):
            if name == '-':
                continue
            normalized_items[name] = count

        return dict(sorted(normalized_items.items(), key=itemgetter(1), reverse=True))
