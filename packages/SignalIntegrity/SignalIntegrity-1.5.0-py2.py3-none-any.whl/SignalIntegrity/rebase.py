"""
rebase.py
"""

# Copyright (c) 2021 Nubis Communications, Inc.
# Copyright (c) 2018-2020 Teledyne LeCroy, Inc.
# All rights reserved worldwide.
#
# This file is part of SignalIntegrity.
#
# SignalIntegrity is free software: You can redistribute it and/or modify it under the terms
# of the GNU General Public License as published by the Free Software Foundation, either
# version 3 of the License, or any later version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY;
# without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
# See the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along with this program.
# If not, see <https://www.gnu.org/licenses/>

import git


branch_list = ['PhaseFix',
               'SPButtonsScroll',
               'SplitFixture',
               'SimulatorNetLists',
               'CLI',
               'cicd',
               'Dispatcher',
               'TextBox',
               'ParserBugs',
               'statistical_noise',
               'MultipleSParameterDisplay',
               'AssortedFeatures',
               'TimeBefore0',
               'EqualizerScripts',
               'BlindEqualization',
               'FileList'
               ]
rebase = False
push_them = True

g=git.cmd.Git('SignalIntegrity')
repo=git.Repo('/home/petep/Work/SignalIntegrity')
repo.git.fetch('origin')

if rebase:
    for branch in branch_list:
        print(f'trying branch {branch}')
        try:
            result = repo.git.checkout(branch)
        except:
            print(f'checkout of {branch} failed!')
            continue
        if result == f"Your branch is up to date with 'origin/{branch}'.":
            result = repo.git.rebase('InNextRelease')
            result = result.split('\n')[-1]
            if 'Applying:' in result:
                continue
            if result == f'Current branch {branch} is up to date.':
                continue
            repo.git.rebase('--abort')

if push_them:
    for branch in branch_list:
        try:
            result = repo.git.checkout(branch)
        except:
            print(f'checkout of {branch} failed!')
            continue
        result = result.split('\n')[0]
        if result == f"Your branch and 'origin/{branch}' have diverged,":
            result = repo.git.push('-f')

if __name__ == '__main__':
    pass