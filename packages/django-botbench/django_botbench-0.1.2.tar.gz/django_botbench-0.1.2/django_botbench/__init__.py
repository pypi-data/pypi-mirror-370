from robo import Bot

class BBBot(Bot):
    """Adds request-based field derivation"""
    
    def derive_field_args_from_scope(self, scope):
        if len(self.fields) != 0:
            raise NotImplementedError(f"Bots with fields are not supported by the default implementation, please override derive_field_args_from_scope(self, scope)")
        return {}
