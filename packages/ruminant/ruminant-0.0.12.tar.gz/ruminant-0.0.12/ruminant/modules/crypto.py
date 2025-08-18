from .. import module, utils, buf
import base64


@module.register
class PdfTimestampSignatureModule(module.RuminantModule):

    def identify(buf):
        with buf:
            buf.skip(27)
            return buf.peek(2) == b"\x30\x82"

    def chew(self):
        meta = {}
        meta["type"] = "pdf-timestamp-signature"

        self.buf.skip(27)
        meta["data"] = utils.read_der(self.buf)

        return meta


@module.register
class DerModule(module.RuminantModule):

    def identify(buf):
        return buf.pu16() & 0xfff0 == 0x3080

    def chew(self):
        meta = {}
        meta["type"] = "der"

        meta["data"] = utils.read_der(self.buf)

        return meta


@module.register
class PemModule(module.RuminantModule):

    def identify(buf):
        return buf.peek(27) == b"-----BEGIN CERTIFICATE-----"

    def chew(self):
        meta = {}
        meta["type"] = "pem"

        self.buf.skip(27)

        content = b""
        while True:
            line = self.buf.rl()
            if line == b"-----END CERTIFICATE-----":
                break

            content += line

        while self.buf.peek(1) in (b"\r", b"\n"):
            self.buf.skip(1)

        meta["data"] = utils.read_der(buf.Buf(base64.b64decode(content)))

        return meta


@module.register
class PgpModule(module.RuminantModule):

    def identify(buf):
        with buf:
            if buf.pu8() in (0x85, 0x89) and buf.peek(4)[3] in (0x03, 0x04):
                return True

            return buf.rl().startswith(b"-----BEGIN PGP ")

    def chew(self):
        meta = {}
        meta["type"] = "pgp"

        if self.buf.peek(1) == b"-":
            if self.buf.rl() == b"-----BEGIN PGP SIGNED MESSAGE-----":
                message = b""

                meta["message-hash"] = self.buf.rl().split(b": ")[1].decode(
                    "utf-8")
                self.buf.rl()

                while True:
                    line = self.buf.rl()

                    if line == b"-----BEGIN PGP SIGNATURE-----":
                        break

                    message += line + b"\n"

                meta["message"] = utils.decode(message).split("\n")[:-1]

            content = b""
            while True:
                line = self.buf.rl()
                if line.startswith(b"-----END PGP "):
                    break

                if line.startswith(b"Comment: "):
                    continue

                content += line

            while self.buf.peek(1) in (b"\r", b"\n"):
                self.buf.skip(1)

            if b"=" in content:
                while content[-1] != b"="[0]:
                    content = content[:-1]

            fd = buf.Buf(base64.b64decode(content))
        else:
            fd = self.buf

        meta["data"] = []
        while fd.available() > 0:
            meta["data"].append(utils.read_pgp(fd))

        return meta
