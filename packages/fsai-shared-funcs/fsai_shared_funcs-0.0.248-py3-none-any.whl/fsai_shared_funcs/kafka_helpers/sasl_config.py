def sasl_conf(args):
    sasl_mechanism = args["kafka_sasl_mechanism"].upper()

    sasl_conf = {
        "sasl.mechanism": sasl_mechanism,
        # Set to SASL_SSL to enable TLS support.
        "security.protocol": "SASL_PLAINTEXT",
    }

    if sasl_mechanism != "GSSAPI":
        sasl_conf.update(
            {
                "sasl.username": args["kafka_user_name"],
                "sasl.password": args["kafka_user_password"],
            }
        )

    if sasl_mechanism == "GSSAPI":
        sasl_conf.update(
            {
                "sasl.kerberos.service.name",
                args["kafka_user_name"],
                # Keytabs are not supported on Windows. Instead the
                # the logged on user's credentials are used to
                # authenticate.
                "sasl.kerberos.principal",
                args["kafka_user_name"],
                "sasl.kerberos.keytab",
                args["kafka_user_password"],
            }
        )

    return sasl_conf
