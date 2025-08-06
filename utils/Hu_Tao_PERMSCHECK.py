import json
import os
from discord.ext import commands

def check_module_perm(module_name):
    async def predicate(ctx):
        try:
            with open(os.path.join("config", "Hu_Tao_permissions.json"), "r") as f:
                perms = json.load(f)
            allowed_roles = perms.get(module_name, [])
            return any(role.name in allowed_roles for role in ctx.author.roles)
        except Exception:
            return False
    return commands.check(predicate)