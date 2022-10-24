# rollingUpdate(replicas) --> (maxSurge, maxUnavailable)


def rollingUpdate(replicas):

    rolling = {
        'maxSurge': divmod(replicas, 4)[0] + 1 if divmod(replicas, 4)[0] + 1 <= divmod(replicas, 2)[0] else 1,
        'maxUnavailable': 0
    }
    return rolling
