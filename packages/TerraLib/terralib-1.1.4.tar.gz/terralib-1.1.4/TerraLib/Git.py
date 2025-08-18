# coding=utf-8

import os
from . import SubProcess
from pathlib import Path

temp_comment = "temp_comment.txt"


class File_Log:
    def __init__(self, fileRev, author, date, timestamp, description):
        self.Revision = fileRev
        self.Author = author
        self.Date = date
        self.TimeStamp = int(timestamp.strip())
        self.Description = description
        self.commit_id = None

    def __repr__(self):
        return f"{self.Revision}\n{self.Author}\n{self.Date}\n{self.TimeStamp}\n{self.Description}"


class GitHelper():
    def __init__(self, remote_repo, workspace, encoding="utf-8"):
        self.remote_repo = remote_repo
        self.workspace = workspace
        self.version = "1.0"
        self.encoding = encoding

    def __run_command(self, command, cwd=None, active_info=True, silent=False, show_cmd=True):
        run_command = SubProcess.RunCMD()
        run_command.active_info = active_info
        run_command.silent = silent
        run_command.show_cmd = show_cmd
        run_command.encoding = self.encoding
        cwd = cwd if cwd else self.workspace

        rc, msg = run_command.run_command(command, cwd, skip_blank_lines=True)
        if rc == SubProcess.RC_CODE.RC_PASS:
            return True, msg
        else:
            return False, msg

    def git_list(self, dir_or_file=None):
        command = 'git ls-tree -r --name-only HEAD'
        if dir_or_file:
            result, output = self.__run_command(command, cwd=dir_or_file)
        else:
            result, output = self.__run_command(command)
        if result:
            print("List successful!")
            return output
        else:
            print("List failed!")
            return None

    def git_fetch_all(self):
        command = "git fetch --all"
        result, output = self.__run_command(command)
        if result:
            return True
        else:
            return False

    def git_get_local_version(self):
        command = "git rev-parse HEAD"
        result, output = self.__run_command(command)
        if result:
            return "".join(output).strip()
        else:
            return None

    def git_get_remote_version(self):
        if self.git_fetch_all():
            command = "git rev-parse origin/HEAD"
            result, output = self.__run_command(command)
            if result:
                return "".join(output).strip()
            else:
                return None
        else:
            return None

    def git_get_local_commit_date(self, ):
        logs = self.git_log(path=None, num=1, more_args="HEAD", cwd=self.workspace)
        if logs:
            return logs[0].TimeStamp
        return None

    def git_get_remote_commit_date(self):
        if self.git_fetch_all():
            logs = self.git_log(path=None, num=1, more_args="origin/HEAD", cwd=self.workspace)
            if logs:
                return logs[0].TimeStamp
        return None

    def git_get_actions(self, first_run=False):
        """
        Added (A)
        Copied (C)
        Deleted (D)
        Modified (M)
        Renamed (R)
        changed (T)
        are Unmerged (U)
        are Unknown (X)
        or have had their pairing Broken (B).
         """
        new_actions = []
        if not os.path.exists(self.workspace):
            first_run = True
        if first_run:
            self.git_clone()
            initial_version = self.git_get_initial_revision()
            local_version = self.git_get_local_version()
            actions = self.git_diff(local_version, initial_version)
        else:
            local_version = self.git_get_local_version()
            remote_version = self.git_get_remote_version()
            if local_version == remote_version:
                return new_actions  # 如果版本一致，则actions为空
            else:
                actions = self.git_diff(remote_version, local_version)
        for action in actions:
            if not (action.strip().startswith("M")
                    or action.strip().startswith("A")
                    or action.strip().startswith("D")
                    or action.strip().startswith("R")):
                continue
            action_act = action.strip().split()[0]
            action_path = action.strip()[len(action_act):].strip()
            if action.strip().startswith("R"):
                rm_file, new_file = [x.strip() for x in action_path.split('\t')]
                new_actions.append(("D", rm_file))
                new_actions.append(("A", new_file))
            else:
                new_actions.append((action_act, action_path))
        return new_actions

    def git_clone(self):
        # clone
        command = f'git clone "{self.remote_repo}" "{self.workspace}"'
        result, output = self.__run_command(command, cwd=os.getcwd(), active_info=True)
        print("".join(output))
        if result:
            return True
        else:
            return False

    def git_merge(self):
        command = f'git merge origin/main'
        result, output = self.__run_command(command, active_info=True)
        print("".join(output))
        if result:
            return True
        else:
            return False

    def git_pull(self):
        command = f'git pull'
        result, output = self.__run_command(command, active_info=True)
        print("".join(output))
        if result:
            return True
        else:
            return False

    def git_get_initial_revision(self):
        command = f"git log --oneline --pretty=%H"
        result, output = self.__run_command(command)
        revisions = [x for x in output if x.strip()]
        if result:
            return revisions[-1].strip()
        else:
            return None

    def git_diff(self, local_version, remote_version):
        diff_actions = []
        pre_set = " git config core.quotepath false"
        command = f"{pre_set} & git diff {remote_version} {local_version} --name-status"
        result, output = self.__run_command(command)
        if result:
            print("Get diff succeed!")
            diff_actions = output
        else:
            print("Get diff failed!")
        return diff_actions

    def git_add(self, path):
        path = Path(path)
        if path.exists():
            command = f'git add "{path}"'
            result, output = self.__run_command(command)
            if result:
                print("Git add successful!")
                return True
            else:
                print("Git add failed!")
                return False
        else:
            return False

    def git_rm(self, path):
        path = Path(path)
        if path.exists():
            command = f'git rm "{path}"'
            result, output = self.__run_command(command)
            if result:
                print("Git rm successful!")
                return True
            else:
                print("Git rm failed!")
                return False
        else:
            return False

    def git_commit(self, path="", comment=""):
        comment_file = self.prepare_comment_file(comment)
        try:
            if path:
                command = f'git commit "{path}" -F "{comment_file}"'
            else:
                command = f'git commit -F "{comment_file}"'
            result, output = self.__run_command(command)
            if result:
                for line in output:
                    print(line)
                print("Commit successful!")
            else:
                for line in output:
                    print(line)
                print("Commit failed!")
            return result
        finally:
            if os.path.exists(comment_file):
                os.remove(comment_file)

    def git_push(self):
        command = f"git push"
        result, output = self.__run_command(command)
        if result:
            print("Git push successful!")
            return True
        else:
            print("Git push failed!")
            print('\n'.join(output))
            return False

    def git_add_commit_push(self, path, comment):
        if self.git_add(path):
            if self.git_commit(path, comment):
                if self.git_push():
                    return True
                else:
                    return False
            else:
                return False
        else:
            return False

    def git_head_revision(self):
        command = "git rev-parse HEAD"
        result, output = self.__run_command(command)
        if result:
            print("Git get head revision successful!")
            return output
        else:
            print("Git get head revision failed!")
            return None

    def git_log(self, path=None, num=100, more_args="", cwd=None):
        logResult = []
        split = "***********************LOGEND*********************"
        if path:
            cmd = f'git log -n {num} --pretty="Revision:%H%nAuthor:%ae%nDate:%ci%nTimeStamp:%ct%nDescription:%B%n{split}" -- "{path}"'
        else:
            cmd = f'git log -n {num} --pretty="Revision:%H%nAuthor:%ae%nDate:%ci%nTimeStamp:%ct%nDescription:%B%n{split}" {more_args}'
        result, output = self.__run_command(cmd, cwd=cwd)
        if result:
            revision = ""
            author = ""
            date = ""
            timestamp = ""
            description = ""
            description_start = False
            for line in output:
                line_text = line.strip()
                if line_text.startswith("Revision:"):
                    revision = line_text[9:]
                elif line_text.startswith("Author:"):
                    author = line_text[7:]
                elif line_text.startswith("Date:"):
                    date = line_text[5:]
                elif line_text.startswith("TimeStamp:"):
                    timestamp = line_text[10:]
                elif line_text.startswith("Description:"):
                    description_start = True
                    description += line.lstrip()[12:]
                elif line_text == split:
                    file_log = File_Log(revision, author, date, timestamp, description.strip())
                    logResult.append(file_log)
                    description_start = False
                    description = ""
                else:
                    if description_start:
                        description += line
        return logResult

    @staticmethod
    def prepare_comment_file(comment):
        with open(temp_comment, "w", encoding="utf-8") as f:
            f.write(comment)
        return os.path.realpath(temp_comment)
