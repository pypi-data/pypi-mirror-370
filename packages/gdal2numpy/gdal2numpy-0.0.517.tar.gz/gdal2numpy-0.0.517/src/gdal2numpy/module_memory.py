# -------------------------------------------------------------------------------
# MIT License:
# Copyright (c) 2012-2023 Luzzi Valerio
#
# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES
# OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
# NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT
# HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY,
# WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR
# OTHER DEALINGS IN THE SOFTWARE.
#
#
# Name:        memory.py
# Purpose:
#
# Author:      Luzzi Valerio
#
# Created:     16/06/2023
# -------------------------------------------------------------------------------
import os
import gc
import psutil
from .module_log import Logger

MAX_MEMORY_USED = 0

def mem_usage():
    """
    mem_usage - return the memory used
    """
    global MAX_MEMORY_USED
    gc.collect()
    # m = psutil.virtual_memory().used / (1024 ** 2) questa è la memoria
    # totale utilizzata dalla macchina
    process = psutil.Process(os.getpid())
    m = process.memory_info().rss
    MAX_MEMORY_USED = max(m, MAX_MEMORY_USED)
    MB = m / (1024**2)
    Logger.debug("Memory used:%.2f MB"%(MB))
    Logger.debug("_______________________")


def max_mem_usage():
    """
    max_mem_usage - return the max memory used
    """
    global MAX_MEMORY_USED
    MB = MAX_MEMORY_USED / (1024**2)
    Logger.debug(f"Max Memory used:{MB:.2f} MB")
    Logger.debug("_______________________")
