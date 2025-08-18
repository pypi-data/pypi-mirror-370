import subprocess
import re
import os
import sys
from distutils.dist import command_re

from . import SubProcess


class File_Info:
    def __init__(self, fileLink, fileName, fileType, revision, lastUpdateTime, lastUpdateAuthor, lockStatus, lockTime,
                 lockAuthor):
        self.FileLink = fileLink
        self.FileName = fileName
        self.FileType = fileType
        self.Revision = revision
        self.LastUpdateTime = lastUpdateTime
        self.LastUpdateAuthor = lastUpdateAuthor
        self.LockStatus = lockStatus
        self.LockTime = lockTime
        self.LockAuthor = lockAuthor


class File_Log:
    def __init__(self, fileRev, author, date, description):
        self.Revision = int(fileRev.strip())
        self.Author = author
        self.Date = date
        self.Description = description


temp_comment = "temp_comment.txt"


class SVN_Helper:
    def __init__(self, repo_url, user, pw, work_copy):
        self.repo_url = repo_url
        self.work_copy = work_copy if work_copy else "."
        self.user = user
        self.pw = pw

        if user and pw:
            self.authority = "--username={0} --password={1}".format(self.user, self.pw)
        else:
            self.authority = ""

    def __bytes2str(self, bytes_data):
        """
        bytes to str
        :param bytes_data:
        :return:
        """
        try:
            return bytes_data.decode("gbk")
        except:
            return bytes_data.decode("utf-8", "ignore")

    def __run_command(self, command, cwd=None, active_info=True, silent=True, show_cmd=True):
        run_command = SubProcess.RunCMD()
        run_command.active_info = active_info
        run_command.silent = silent
        run_command.show_cmd = show_cmd
        result, msg = run_command.run_command(command, cwd=cwd)
        if result:
            return True, msg
        else:
            return False, msg

    def svn_list(self, dir_or_file=None, exit_on_error=False):
        if dir_or_file:
            command = 'svn ls "{dir_or_file}" -R {authority}'.format(dir_or_file=dir_or_file,
                                                                     authority=self.authority)
        else:
            command = 'svn ls -R {authority}'.format(authority=self.authority)
        result, output = self.__run_command(command)
        if result:
            print("List successful!")
            return output
        else:
            print("List failed!")
            if exit_on_error:
                exit(1)
            return None

    def svn_add(self, dir_or_file=None, exit_on_error=False, silent=False):
        if dir_or_file:
            command = 'svn add "{dir_or_file}" --force {authority}'.format(dir_or_file=dir_or_file,
                                                                           authority=self.authority)
        else:
            command = 'svn add * --force {authority}'.format(authority=self.authority)
        result, output = self.__run_command(command, show_cmd=not silent, active_info=not silent, silent=silent)
        if result:
            if not silent:
                print("Add successful!")
        else:
            print("Add failed!")
        return result

    def svn_delete(self, dir_or_file, exit_on_error=False, silent=False):
        command = 'svn delete "{dir_or_file}" --force {authority}'.format(dir_or_file=dir_or_file,
                                                                          authority=self.authority)
        result, output = self.__run_command(command, show_cmd=not silent, active_info=not silent, silent=silent)
        if result:
            if not silent:
                print("Delete successful!")
        else:
            print("Delete failed!")
            if exit_on_error:
                exit(1)
        return result

    def svn_lock(self, fileUrl, exit_on_error=False):
        command = 'svn lock "{fileUrl}" {authority}'.format(fileUrl=fileUrl, authority=self.authority)
        result, output = self.__run_command(command)
        if result:
            print("Lock successful!")
        else:
            print("Lock failed!")
            if exit_on_error:
                exit(1)
        return result

    def svn_unlock(self, fileUrl, exit_on_error=False):
        command = 'svn unlock "{fileUrl}" {authority}'.format(fileUrl=fileUrl, authority=self.authority)
        result, output = self.__run_command(command)
        if result:
            print("Unlock successful!")
        else:
            print("Unlock failed!")
            if exit_on_error:
                exit(1)
        return result

    def svn_commit(self, file="", comment="", exit_on_error=False, silent=False):
        comment_file = self.prepare_comment_file(comment)
        try:
            if file:
                command = 'svn ci "{file}" -F "{comment}" {authority}'.format(file=file, comment=comment_file,
                                                                              authority=self.authority)
            else:
                command = 'svn ci -F "{comment}" {authority}'.format(comment=comment_file, authority=self.authority)
            result, output = self.__run_command(command, show_cmd=not silent, active_info=not silent, silent=silent)
            if result:
                if not silent:
                    print("Commit successful!")
            else:
                print("Commit failed!")
                if exit_on_error:
                    exit(1)
        finally:
            if os.path.exists(comment_file):
                os.remove(comment_file)

    def svn_commit_files(self, files, comment="", depth="", exit_on_error=False, silent=False):
        comment_file = self.prepare_comment_file(comment)
        try:
            commit_files = " ".join([f'"{x}"' for x in files])
            command = f'svn ci {depth} {commit_files} -F "{comment_file}" {self.authority}'
            result, output = self.__run_command(command, show_cmd=not silent, active_info=not silent, silent=silent)
            if result:
                print("Commit successful!")
                for line in output:
                    if line.strip().startswith("Committed revision"):
                        commit_revision = re.sub("^Committed revision (\d+).*$", "\\1", line)
                        return commit_revision
            else:
                print("Commit failed!")
                if exit_on_error:
                    exit(1)
        finally:
            if os.path.exists(comment_file):
                os.remove(comment_file)

    def svn_log(self, fileUrl, level=100):
        logResult = []
        command = 'svn log "{fileUrl}" -l {level} {authority}'.format(fileUrl=fileUrl, level=level,
                                                                      authority=self.authority)
        result, output = self.__run_command(command)
        if result:
            str_line = ''
            for line in output:
                str_line += line.strip() + '|'
            new_lines = str_line.split('------------------------------------------------------------------------')
            for new_line in new_lines:
                new_line = new_line.strip('|')
                if new_line.strip() != "":
                    parts = new_line.split('|')
                    description = ''
                    for i in range(5, len(parts)):
                        description += parts[i] + "\n"
                    rev = re.sub("^r(\d+)$", "\\1", parts[0].strip())
                    author = parts[1].strip()
                    date = re.sub('.*?(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}).*?', "\\1", parts[2])
                    description = description.strip()
                    fileLog = File_Log(rev, author, date, description)
                    logResult.append(fileLog)
        return logResult

    def svn_remote_files(self, folderUrl=None, suffix=None):
        completeFiles = []
        folderUrl = folderUrl if folderUrl else self.repo_url
        command = f'svn ls "{folderUrl}" -R {self.authority}'
        result, output = self.__run_command(command)
        if result:
            for file in output:
                if file.strip():
                    file_extension = os.path.splitext(file)[1].lower()
                    if isinstance(suffix, list):
                        if file_extension in suffix:
                            if file.strip():
                                completeFiles.append(folderUrl.strip("/") + "/" + file)
                    else:
                        completeFiles.append(folderUrl.strip("/") + "/" + file)
        return completeFiles

    def svn_file_info(self, fileUrl):
        command = 'svn info "{fileUrl}" {authority}'.format(fileUrl=fileUrl, authority=self.authority)
        result, output = self.__run_command(command)
        fileName = os.path.basename(fileUrl)
        fileType = None
        revision = 0
        lastUpdateTime = ""
        lastUpdateAuthor = ""
        lockStatus = ""
        lockTime = ""
        lockAuthor = ""
        if result:
            for line in output:
                if line.startswith("URL:"):
                    fileUrl = line[4:].strip()
                if line.startswith("Node Kind:"):
                    fileType = line[10:].strip()
                if line.startswith("Last Changed Rev:"):
                    revision = line[18:].strip()
                if line.startswith("Last Changed Author:"):
                    lastUpdateAuthor = line[20:40].strip()
                if line.startswith("Last Changed Date:"):
                    lastUpdateTime = line[18:38].strip()
                if line.startswith("Lock Owner:"):
                    lockStatus = '<font color="blue">Locked</font>'
                    lockAuthor = line[12:].strip()
                if line.startswith("Lock Created:"):
                    lockTime = line[14:34].strip()
            fileInfo = File_Info(fileUrl, fileName, fileType, revision, lastUpdateTime, lastUpdateAuthor, lockStatus,
                                 lockTime,
                                 lockAuthor)
            return fileInfo

    def svn_checkout(self, folderUrl=None, exit_on_error=False, silent=False):
        folderUrl = folderUrl if folderUrl else self.repo_url
        actions = []
        command = f'svn co "{folderUrl}" {self.work_copy} {self.authority}'
        result, output = self.__run_command(command, show_cmd=not silent, active_info=not silent, silent=silent)
        if result:
            if not silent:
                print("Check out repo_url:{0} succeed!".format(folderUrl))
            for line in output:
                actions.append(line.replace(self.work_copy + "\\", ""))
        else:
            print("Check out repo_url: {0} failed!".format(folderUrl))
            if exit_on_error:
                exit(1)
        return actions

    def svn_get_remote_version(self):
        revision = self.svn_file_info(self.repo_url).Revision
        print("Remote version:{0}".format(revision))
        return revision

    def svn_get_local_version(self):
        revision = self.svn_file_info(self.work_copy).Revision
        print("Local version:{0}".format(revision))
        return revision

    def svn_revert(self, dir_or_file=None, recursive=True, silent=False):
        dir_or_file = dir_or_file if dir_or_file else self.work_copy
        recursive = "-R" if recursive else ""
        if not os.path.exists(dir_or_file):
            return self.svn_update(dir_or_file)
        else:
            command = f'svn revert {recursive} "{dir_or_file}" {self.authority}'
            result, output = self.__run_command(command, show_cmd=not silent, active_info=not silent, silent=silent)
            if result:
                if not silent:
                    print(f"Revert {dir_or_file} succeed!")
            else:
                print(f"Revert {dir_or_file} failed!")
            return result

    def svn_clenup(self, dir_path, exit_on_error=False, silent=False):
        command = f'svn cleanup "{dir_path}" {self.authority}'
        result, output = self.__run_command(command, show_cmd=not silent, active_info=not silent, silent=silent)
        if result:
            if not silent:
                print(f"[Succeed] Cleanup [{dir_path}]")
        else:
            print("[Failed] Cleanup [{dir_path}]")
            if exit_on_error:
                exit(1)
        return result

    def svn_update(self, dir_or_file=None, more_args="", exit_on_error=False, silent=False):
        dir_or_file = dir_or_file if dir_or_file else self.work_copy
        command = f'svn update "{dir_or_file}" {more_args} {self.authority}'
        result, output = self.__run_command(command, show_cmd=not silent, active_info=not silent, silent=silent)
        if result:
            if not silent:
                print("Update:{0} succeed!".format(dir_or_file))
        else:
            print("Update:{0} failed!".format(dir_or_file))
            if exit_on_error:
                sys.exit(1)
        return result

    def svn_update_to(self, revision, dir_or_file=None, more_args="", exit_on_error=False, silent=False):
        dir_or_file = dir_or_file if dir_or_file else self.work_copy
        local_revision = self.svn_file_info(dir_or_file).Revision
        if str(revision).strip() == str(local_revision).strip():
            print(f"Update Ignored: Self:{revision}({local_revision}) : {dir_or_file}")
            return True
        else:
            command = f'svn update "{dir_or_file}" -r {revision} {more_args} {self.authority}'
            result, output = self.__run_command(command, show_cmd=not silent, active_info=not silent, silent=silent)
            if result:
                for line in output:
                    update_p = "(?:(?:updated to)|(?:at)) revision (\d+).*"
                    if re.fullmatch(update_p, line.strip(), flags=re.I):
                        repo_revision = re.sub(update_p, "\\1", line.strip(), flags=re.I)
                        act_revision = self.svn_file_info(dir_or_file).Revision
                        if not silent:
                            print(
                                f"Update Succeed: Self:{revision}({act_revision}) Repo:{repo_revision} : {dir_or_file}")
                        return result
                print("Update Failed:{0} to revision {1} failed!".format(dir_or_file, revision))
                if exit_on_error:
                    sys.exit(1)
                return result
            else:
                print("Update Failed:{0} to revision {1} failed!".format(dir_or_file, revision))
                if exit_on_error:
                    sys.exit(1)
            return result

    def svn_diff(self, local_version, remote_version):
        diff_actions = []
        command = "svn diff -r {local_version}:{remote_version} --summarize {authority}".format(
            local_version=local_version, remote_version=remote_version, authority=self.authority)
        result, output = self.__run_command(command)
        if result:
            print("Get diff succeed!")
            diff_actions = output
        else:
            print("Get diff failed!")
        return diff_actions

    def svn_get_actions(self, first_run=False):
        new_actions = []
        if first_run:
            actions = self.svn_checkout()
        else:
            local_version = self.svn_get_local_version()
            remote_version = self.svn_get_remote_version()
            if local_version == remote_version:
                return new_actions  # 如果版本一致，则actions为空
            else:
                actions = self.svn_diff(local_version, remote_version)
        for action in actions:
            if not (action.strip().startswith("M") or action.strip().startswith("A") or action.strip().startswith("D")):
                continue
            action_act = action.strip().split()[0]
            action_path = action.strip()[1:].strip()
            new_actions.append((action_act, action_path))
        return new_actions

    def svn_status(self, path, show_cmd=True, silent=False):
        command = f"svn status {path} {self.authority}"
        result, output = self.__run_command(command, show_cmd=show_cmd, silent=silent)
        return result, output

    def svn_isLatest(self, file):
        local_file_info = self.svn_file_info(file)
        local_revision = local_file_info.Revision
        remote_revision = self.svn_file_info(local_file_info.FileLink).Revision
        if remote_revision == local_revision:
            return True
        else:
            return False

    def svn_cat(self, path, revision="HEAD", show_cmd=True, silent=False):
        command = f"svn cat {path} -r {revision} {self.authority}"
        result, output = self.__run_command(command, show_cmd=show_cmd, silent=silent)
        return result, output

    @staticmethod
    def check_file_svn_version(file):
        svn = SVN_Helper(None, None, None, None)
        result = True
        try:
            result = svn.svn_isLatest(os.path.realpath(file))
        except:
            pass
        if not result:
            print("This file is not latest,please svn update below folder at first!")
            print("%s\n" % os.path.dirname(os.path.realpath(file)))
            sys.exit(1)

    @staticmethod
    def prepare_comment_file(comment):
        with open(temp_comment, "w", encoding="utf-8") as f:
            f.write(comment)
        return os.path.realpath(temp_comment)

    @staticmethod
    def svn_checkout_by_folder_list(repo, workspace_root, folder_list, exit_on_error=False):
        if os.path.exists(workspace_root):
            print(f"Workspace:[{workspace_root}] already existed!")
            return
        svn = SVN_Helper(None, None, None, None)
        # step1 create workspace
        cmd1 = f'svn co "{repo}" "{workspace_root}" --depth=empty'
        mycmd = SubProcess.RunCMD()
        mycmd.active_info = True
        rc, msg = mycmd.run_command(cmd1, cwd=os.getcwd())
        if rc == SubProcess.RC_CODE.RC_PASS:
            folder_list = sorted(folder_list, key=lambda x: x[0])
            # update all file_folders infinity
            for folder, update_args in folder_list:
                folder_real = os.path.realpath(os.path.join(workspace_root, folder.strip("/")))
                if not SVN_Helper.update_by_levels(svn, folder_real, update_args=update_args):
                    if exit_on_error:
                        sys.exit(1)
                    return False
        else:
            if exit_on_error:
                sys.exit(1)
            return False

    @staticmethod
    def update_by_levels(svn, name, revision="HEAD", islast=True, exit_on_error=False, update_args="--depth=infinity"):
        head, tail = os.path.split(name)
        if not tail:
            head, tail = os.path.split(head)
        if head and tail and not os.path.exists(head):
            if not SVN_Helper.update_by_levels(svn, head, revision=revision, islast=False, exit_on_error=exit_on_error,
                                               update_args=update_args):
                return False
        if islast:
            cmd = f'svn up "{name}" --r {revision} {update_args}'
        else:
            cmd = f'svn up "{name}" --depth=empty'
        mycmd = SubProcess.RunCMD()
        mycmd.active_info = True
        rc, msg = mycmd.run_command(cmd)
        if rc == SubProcess.RC_CODE.RC_PASS:
            return True
        else:
            if exit_on_error:
                sys.exit(1)
            return False
