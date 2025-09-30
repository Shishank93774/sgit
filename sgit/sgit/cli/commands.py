"""Command implementations with lazy imports to avoid circular dependencies."""

def cmd_init(args):
    from ..operations.init import cmd_init as _cmd_init
    _cmd_init(args)

def cmd_cat_file(args):
    from ..utils.hashing import cmd_cat_file as _cmd_cat_file
    _cmd_cat_file(args)

def cmd_check_ignore(args):
    from ..utils.ignore import cmd_check_ignore as _cmd_check_ignore
    _cmd_check_ignore(args)

def cmd_checkout(args):
    from ..operations.checkout import cmd_checkout as _cmd_checkout
    _cmd_checkout(args)

def cmd_commit(args):
    from ..operations.commit import cmd_commit as _cmd_commit
    _cmd_commit(args)

def cmd_hash_object(args):
    from ..utils.hashing import cmd_hash_object as _cmd_hash_object
    _cmd_hash_object(args)

def cmd_log(args):
    from ..operations.log import cmd_log as _cmd_log
    _cmd_log(args)

def cmd_ls_files(args):
    from ..core.index import cmd_ls_files as _cmd_ls_files
    _cmd_ls_files(args)

def cmd_ls_tree(args):
    from ..core.index import cmd_ls_tree as _cmd_ls_tree
    _cmd_ls_tree(args)

def cmd_rev_parse(args):
    from ..core.refs import cmd_rev_parse as _cmd_rev_parse
    _cmd_rev_parse(args)

def cmd_rm(args):
    from ..operations.add_remove import cmd_rm as _cmd_rm
    _cmd_rm(args)

def cmd_status(args):
    from ..operations.status import cmd_status as _cmd_status
    _cmd_status(args)

def cmd_tag(args):
    from ..core.refs import cmd_tag as _cmd_tag
    _cmd_tag(args)

def cmd_add(args):
    from ..operations.add_remove import cmd_add as _cmd_add
    _cmd_add(args)