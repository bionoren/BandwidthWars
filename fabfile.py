from fabric.api import run, sudo, env, settings, local
from fabric.context_managers import cd
import fabric
import scissors
env.use_ssh_config = True
DEBIAN = "debian"

WORKING_TREE="bandwidthwars"

def server_install():
    if scissors.what_system() == DEBIAN:
        run('apt-get update')
        run('apt-get -y install sudo')
        scissors.debian_upgrade()
    else:
        pass
    scissors.install_python()
    scissors.install_git()
    scissors.install_python_worker_tools()
    print "server is now setup; you need code_drop and a git push to begin"

def code_drop():
	scissors.code_drop(WORKING_TREE)

def emergency_start():
	scissors.emergency_start(WORKING_TREE)

def get_logs():
	scissors.get_logs(WORKING_TREE)
	scissors.get_logs(WORKING_TREE+"game.log")

def show_logs():
	scissors.show_logs(WORKING_TREE)

def show_gamelog():
	run("tail -f %s/game.log" % WORKING_TREE)
