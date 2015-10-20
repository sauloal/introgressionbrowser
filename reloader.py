#!/usr/bin/python

#https://raw.githubusercontent.com/seb-m/pyinotify/master/python2/examples/daemon.py
#https://github.com/seb-m/pyinotify/blob/master/python2/examples/autocompile.py
# Example: daemonize pyinotify's notifier.
#
# Requires Python >= 2.5
import subprocess
import functools
import sys
import os
import pty
import pyinotify
import time
import tempfile

from threading  import Thread

try:
    from Queue import Queue, Empty
except ImportError:
    from queue import Queue, Empty  # python 3.x

ON_POSIX = 'posix' in sys.builtin_module_names

print "PID", os.getpid()

TMP_FOLDER   = '/tmp'
self_name    = os.path.basename(__file__)
self_log     = '%s/%s_%d.log' % (TMP_FOLDER, self_name, os.getpid())
self_pid     = '%s/%s_%d.pid' % (TMP_FOLDER, self_name, os.getpid())



#http://stackoverflow.com/questions/375427/non-blocking-read-on-a-subprocess-pipe-in-python
def enqueue_output(out, queue):
    for line in iter(out.readline, b''):
        queue.put(line)

    print "closing queue", out

class OnWriteHandler(pyinotify.ProcessEvent):
    """
    Simple counter.
    """
    def __init__(self, script, data, log=self_log, auto=True, extensions=['.sqlite', '.nfo', '.py']):
        self.count      = 0
        self.script     = os.path.abspath(script)
        self.bn         = os.path.basename(self.script)
        self.data       = os.path.abspath(data) + '/'
        self.log        = log
        self.auto       = auto
        self.extensions = extensions
        self.cwd        = os.path.dirname(self.script)
        self.magic_name = os.path.join( os.path.abspath(self.data), self_name + '.killer' )
        self.pid        = os.getpid()

        if os.path.exists(self.magic_name):
            os.remove(self.magic_name)

        with open(self.magic_name, 'w') as fhd:
            fhd.write(str(self.pid))

        sys.stdout.write("Handler: count %d script %s basename %s data %s log %s auto %s extensions %s cwd %s magic name %s pid %d\n" %
                         (self.count, self.script, self.bn, self.data, self.log, str(self.auto), ', '.join(self.extensions), self.cwd, self.magic_name, self.pid))

    def _plusone(self):
        self.count += 1

        self._kill_others()

        sys.stdout.write("  running\n")
        sys.stdout.flush()

        #log  = "%s.%s.log" % ( self.log, self.bn )
        #l    = open(log, 'w')
        #sys.stdout.write("   log : %s\n" % log)

        #cmd  = " ".join([self.script, self.data, ' &>> ', self.log])
        cmd  = ['python', self.script, self.data]#, ' 1>>log.o.log 2>>log.e.log']
        sys.stdout.write("   cmd : %s\n" % " ".join(cmd))

        newpid = os.fork()
        if newpid == 0:
            print "calling system"

            """
            try:
                process = subprocess.Popen( " ".join(cmd), shell=True, bufsize=1, stdout=subprocess.PIPE, stderr=subprocess.PIPE )

            except subprocess.CalledProcessError as e:
                print e
                print e.retcode
                print e.cmd
                print e.output
                raise

            print "called system waiting"

            r = process.wait()

            print "called system finished", r, process.poll()
            c = process.communicate()
            print c[0]
            print c[1]
            """


            sys.stdout.write("  child pid %d\n" % os.getpid())

            proc = subprocess.Popen(cmd, cwd=self.cwd, bufsize=1, close_fds=False, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

            qo = None
            to = None
            qe = None
            te = None
            if proc.stdout:
                sys.stdout.write("  child pid %d. starting stdout queue\n" % os.getpid())
                #print proc.stdout
                qo = Queue()
                to = Thread(target=enqueue_output, args=(proc.stdout, qo))
                to.daemon = True # thread dies with the program
                to.start()
                #print proc.stdout
                sys.stdout.write("  child pid %d. started  stdout queue\n" % os.getpid())

            if proc.stderr:
                sys.stdout.write("  child pid %d. starting stderr queue\n" % os.getpid())
                #print proc.stderr
                qe = Queue()
                te = Thread(target=enqueue_output, args=(proc.stderr, qe))
                te.daemon = True # thread dies with the program
                te.start()
                #print proc.stderr
                sys.stdout.write("  child pid %d. started  stderr queue\n" % os.getpid())

            sys.stdout.write("  child pid %d. looping over queue\n" % os.getpid())
            while proc.poll() is None:
                #print "pool start", proc.poll()
                if qo:
                    #print "o", proc.stdout
                    while not qo.empty():
                        line = qo.get_nowait() # or q.get(timeout=.1)
                        if line != '':
                            print line,

                if qe:
                    #print "e", proc.stderr
                    while not qe.empty():
                        line = qe.get_nowait() # or q.get(timeout=.1)
                        if line != '':
                            print line,

                #print "pool end  ", proc.poll()
                time.sleep(.1)
                #print

            sys.stdout.write("  process finished %s return %s\n" % (str(proc.poll()), proc.returncode))

            if qo:
                sys.stdout.write("  process finished %s return %s joning stdout\n" % (str(proc.poll()), proc.returncode))
                print "STDOUT", proc.stdout
                print "STDOUT", proc.stdout.read()
                to.join()
                proc.stdout.close()

            if qe:
                sys.stdout.write("  process finished %s return %s joning stderr\n" % (str(proc.poll()), proc.returncode))
                print "STDERR", proc.stderr
                print "STDERR", proc.stderr.read()
                te.join()
                proc.stderr.close()

            sys.stdout.write("  END EXITING\n")

            if proc.wait() !=0 : pass

            sys.exit(proc.poll())


        else:
            sys.stdout.write("  run\n")

        #l.flush()

        sys.stdout.flush()

    def _kill_others(self):
        sys.stdout.write("  KILLING OTHERS %s\n" % self.bn)

        cmd = 'ps -aux | grep "%s %s" | gawk "{print \$2}" | grep -v %d | tee | xargs -L 1 -t kill -9' % (self.script, self.data, self.pid)
        sys.stdout.write("  CMD: %s\n" % cmd)

        proc = subprocess.Popen(cmd, cwd=self.cwd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

        if proc.wait() !=0 : pass
        #sys.stdout.write("  PASS\n")

        #stdout, stderr = process.communicate()

        #sys.stdout.write("  OUT:\n" + stdout)
        #sys.stdout.write("  ERR:\n" + stderr)
        sys.stdout.write("  KILLED OTHERS\n")
        sys.stdout.flush()

    def _process(self, event):
        sys.stdout.write("Loop %d Start: %s\n"    % (self.count, event.pathname) )

        if os.path.abspath(event.pathname) == self.magic_name:
           sys.stdout.write("MAGIC FILE MODIFIED: %s\n" % self.magic_name)
           sys.stdout.write(" killing ibrowser\n" )
           self._kill_others()
           #sys.stdout.write(" killing other selves\n" )
           #kill_others()
           sys.stdout.write(" quitting\n" )
           sys.stdout.flush()
           sys.exit(0)

        if all(not event.pathname.endswith(ext) for ext in self.extensions):
            sys.stdout.write(" Invalid File %s\n" % event.pathname)
            sys.stdout.write("Loop %d End\n"      % self.count    )
            sys.stdout.flush()
            return

        sys.stdout.write(" Valid File %s\n"   % event.pathname)
        self._plusone()
        sys.stdout.write("Loop %d End\n"      % self.count    )
        sys.stdout.flush()

    def process_IN_MODIFY(self, event):
        sys.stdout.write("EV MODIFY\n" )
        self._process(event)

    def process_IN_ATTRIB(self, event):
        sys.stdout.write("EV ATTR\n" )
        self._process(event)

    def process_IN_CREATE(self, event):
        sys.stdout.write("EV CREATE\n" )
        self._process(event)

    def process_IN_DELETE(self, event):
        sys.stdout.write("EV DELETE\n" )
        self._process(event)

    def process_IN_DELETE_SELF(self, event):
        sys.stdout.write("EV DELETE SELF\n" )
        self._process(event)

    def process_IN_MOVED_TO(self, event):
        sys.stdout.write("EV MOVED TO\n" )
        self._process(event)


def kill_others():
    if os.path.exists(self_pid):
        pid = open(self_pid).read().strip()
        sys.stdout.write("killing self. PID: %d\n" % int(pid))
        subprocess.Popen(['kill', '-9', pid])
        sys.stdout.write("killed self\n")
        os.remove(self_pid)
        sys.stdout.write("removed pid file\n")
        sys.stdout.flush()


if __name__ == '__main__':
    try:
        script_name  = os.path.abspath(sys.argv[1])
        data_path    = os.path.abspath(sys.argv[2])

    except:
        print "%s <script> <data dir>" % sys.argv[0]
        sys.exit(1)

    daemonize    = False
    auto         = True
    extensions   = ['.sqlite', '.nfo', '.py']

    wm           = pyinotify.WatchManager()
    handler      = OnWriteHandler(script=script_name, data=data_path, log=self_log, auto=auto, extensions=extensions)
    notifier     = pyinotify.Notifier(wm, default_proc_fun=handler)
    wm.add_watch(data_path, pyinotify.ALL_EVENTS)

    #on_loop_func = functools.partial(on_loop)

    # Notifier instance spawns a new process when daemonize is set to True. This
    # child process' PID is written to /tmp/pyinotify.pid (it also automatically
    # deletes it when it exits normally). Note that this tmp location is just for
    # the sake of the example to avoid requiring administrative rights in order
    # to run this example. But by default if no explicit pid_file parameter is
    # provided it will default to its more traditional location under /var/run/.
    # Note that in both cases the caller must ensure the pid file doesn't exist
    # before this method is called otherwise it will raise an exception.
    # /tmp/pyinotify.log is used as log file to dump received events. Likewise
    # in your real code choose a more appropriate location for instance under
    # /var/log (this file may contain sensitive data). Finally, callback is the
    # above function and will be called after each event loop.

    sys.stdout.write("going to background\n")

    try:
        notifier.loop(daemonize=daemonize, pid_file=self_pid, stdout=self_log, stderr=self_log)

    except pyinotify.NotifierError, err:
        print >> sys.stderr, err

    print "Exiting"
