from .base import Experiment

import os


class UMRose(Experiment):
    type = "um-rose"

    def __init__(self, path):
        super().__init__(path)

    def find_files(self):
        """
        Finds UM format files in a Rose run
        """
        import mule

        os.environ["UMDIR"] = "/g/data/access/projects/access/umdir"
        rel_path = "share/data/History_Data"
        path = os.path.join(self.path, rel_path)

        for root, dir, files in os.walk(path):
            for f in files:
                p = os.path.join(root, f)
                try:
                    mule.load_umfile(p)
                    yield os.path.relpath(p, self.path)
                except ValueError:
                    # Not a UM file
                    continue

    def identify_streams(self, files):
        """
        Group files into streams with the same variables
        """
        streams = {}

        for f in files:
            s = os.path.basename(f)[:9]
            if s in streams:
                streams[s].append(f)
            else:
                streams[s] = [f]

        return streams

    def find_variables(self, file):
        """
        Find the variables in a single file

        Since all files in a stream share the same variable, this only needs to
        be run once per stream
        """
        import iris

        cubes = iris.load(os.path.join(self.path, file))

        results = [str(c.attributes["STASH"]) for c in cubes]

        return results


class UMUMUI(Experiment):
    type = "um-umui"
