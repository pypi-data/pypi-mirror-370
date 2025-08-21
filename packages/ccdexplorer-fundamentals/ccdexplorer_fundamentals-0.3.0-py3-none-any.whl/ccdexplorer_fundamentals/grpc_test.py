# import ssl
# from OpenSSL import crypto
# import grpc
# import os

# ssl_context = ssl.create_default_context()
# certs_der = ssl_context.get_ca_certs(binary_form=True)
# certs_x509 = [crypto.load_certificate(crypto.FILETYPE_ASN1, x) for x in certs_der]
# certs_pem = [crypto.dump_certificate(crypto.FILETYPE_PEM, x) for x in certs_x509]
# certs_bytes = b"".join(certs_pem)

# cred = grpc.ssl_channel_credentials(certs_bytes)


# # configure this dict for your systems
# system_certs_map = {
#     "Windows": "<Path to system cert>",
#     "Darwin": "/opt/homebrew/etc/ca-certificates/cert.pem",
#     "Linux": "/etc/ssl/certs/ca-bundle.crt",
# }

# os.environ["GRPC_DEFAULT_SSL_ROOTS_FILE_PATH"] = system_certs_map["Darwin"]
# channel_credentials = grpc.ssl_channel_credentials()

# channel = grpc.secure_channel(
#     "grpc.devnet-plt-alpha.concordium.com:20000", channel_credentials
# )
# try:
#     grpc.channel_ready_future(channel).result(timeout=1)

# except grpc.FutureTimeoutError:
#     print("Channel not ready within timeout period.")
