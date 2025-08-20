import libvirt


def request_cred(user: str, password: str):
    """Callback function for authentication"""

    def inner(credentials: list, user_data):  # pylint: disable=unused-argument
        for credential in credentials:
            if credential[0] == libvirt.VIR_CRED_AUTHNAME:
                credential[4] = user
            elif credential[0] == libvirt.VIR_CRED_PASSPHRASE:
                credential[4] = password
        return 0

    return inner
