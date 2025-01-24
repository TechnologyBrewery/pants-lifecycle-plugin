from lifecycle_plugin import lifecycle_plugin #, lifecycle_rules


def rules():
    return [
        *lifecycle_plugin.rules(), 
        # *lifecycle_rules.rules()
    ]