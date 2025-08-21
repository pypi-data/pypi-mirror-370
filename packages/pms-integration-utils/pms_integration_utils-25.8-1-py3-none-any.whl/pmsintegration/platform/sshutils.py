import sshtunnel
from pydantic import BaseModel


class SSHTunnelConfig(BaseModel):
    host: str
    port: int = 22
    auth_mechanism: str = "basic"
    username: str | None = None
    password: str | None = None
    private_key: str | None = None

    def new_tunnel_server(self, remote_host: str, remote_port: int):
        return sshtunnel.open_tunnel(
            ssh_address_or_host=self.host,
            ssh_port=self.port,
            block_on_close=False,
            ssh_username=self.username,
            ssh_password=self.password,
            remote_bind_address=(remote_host, remote_port),
        )


def resolve_localhost(local_bind_address: str) -> str:
    return "localhost" if local_bind_address in ("127.0.0.1", "0.0.0.0") else local_bind_address
