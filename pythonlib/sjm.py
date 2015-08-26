class Job:

    time=None
    memory=None
    queue=None
    project=None
    status=None
    log_dir=None
    cmd_prefix=None
    cmd_separator='&&'
    name_prefix=None
    sge_options=None

    def __init__(self, name=None):
        self.name=name
        if self.name_prefix is not None and self.name is not None:
            self.name=self.name_prefix+self.name
        self.status=None
        self.cmds=[]
        self.dependents=[]

    def __str__(self):
        s='job_begin\n'
        if self.name is not None:
            s+='    name %s\n'%self.name
        if self.time is not None:
            s+='    time %s\n'%self.time
        if self.memory is not None:
            s+='    memory %s\n'%self.memory
        if self.queue is not None:
            s+='    queue %s\n'%self.queue
        if self.project is not None:
            s+='    project %s\n'%self.project
        if self.status is not None:
            s+='    status %s\n'%self.status
        if self.sge_options is not None:
            s+='    sge_options %s\n'%self.sge_options
        if len(self.cmds)>0:
            s+='    cmd_begin\n'
            #s += '    cmd '
            if self.cmd_separator is None:
                seperator = '\n'
            else:
                seperator = self.cmd_separator
            cmd_prefix = '' if self.cmd_prefix is None else self.cmd_prefix
            cmd_strs = ['       %s %s' % (cmd_prefix, cmd) for cmd in self.cmds]
            s+=seperator.join(cmd_strs) + '\n'
            s+='    cmd_end\n'
        s+='job_end\n'
        return s

    def done(self):
        self.status='done'

    def append(self, cmd):
        self.cmds.append(cmd)
        return self

    def depend(self, *jobs):
        if jobs is not None:
            for job in jobs:
                if job is not None:
                    self.dependents.append(job)
        return self

    def order(self, history=[]):
        s=''
        for dependent in self.dependents:
            s+=dependent.order(history)
            order=(dependent.name, self.name)
            if self.name is not None and order not in history:
                s+= "order %s before %s\n" % order
                history.append(order)
        return s

    def traverse(self, history=[]):
        s=''
        for dependent in self.dependents:
            s+=dependent.traverse(history)
        if self.name is not None and self not in history:
            s+=str(self)
        history.append(self)
        return s

    def desc(self):
        s=self.traverse()
        s+=self.order()
        if self.log_dir is not None:
            s+='log_dir %s\n'%self.log_dir
        return s
