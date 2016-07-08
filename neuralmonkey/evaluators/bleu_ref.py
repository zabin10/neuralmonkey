import tempfile
import subprocess
import os

class BLEUReferenceImplWrapper(object):
    """Wrapper for TectoMT's wrapper for reference NIST and BLEU scorer"""

    def __init__(self, wrapper, name="BLEU", encoding="utf-8"):
        self.wrapper = wrapper
        self.encoding = encoding
        self.name = name


    def serialize_to_bytes(self, sentences):
        # type: (List[List[str]]) -> bytes
        joined = [" ".join(r) for r in sentences]
        string = "\n".join(joined) + "\n"
        return string.encode(self.encoding)


    def __call__(self, decoded, references):
        # type: (List[List[str]], List[List[str]]) -> float

        ref_bytes = self.serialize_to_bytes(references)
        dec_bytes = self.serialize_to_bytes(decoded)

        reffile = tempfile.NamedTemporaryFile()
        reffile.write(ref_bytes)
        reffile.flush()

        output_proc = subprocess.run(["perl", self.wrapper, reffile.name],
                                     input=dec_bytes,
                                     stderr=subprocess.PIPE,
                                     stdout=subprocess.PIPE)

        proc_stdout = output_proc.stdout.decode("utf-8")
        lines = proc_stdout.splitlines()

        try:
            fl = float(lines[0])
            return fl
        except ValueError:
            print("Value error - bleu '{}' is not a number.".format(lines[0]))
            return 0.0