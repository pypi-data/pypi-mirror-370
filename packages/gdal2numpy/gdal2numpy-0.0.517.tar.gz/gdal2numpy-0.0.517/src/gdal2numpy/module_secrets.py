# -------------------------------------------------------------------------------
# MIT License:
# Copyright (c) 2012-2022 Luzzi Valerio
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
# Name:        module_secrets.py
# Purpose:
#
# Author:      Luzzi Valerio
#
# Created:     17/10/2024
# -------------------------------------------------------------------------------
import os
from .filesystem import juststem

def load_secret(filename, varname=None):
    """
    load_secret
    """
    # Auto-complete the path
    if filename and not filename.startswith("/run/secrets/"):
        filename = f"/run/secrets/{filename}"

    if filename and os.path.isfile(filename):
        with open(filename, "r", encoding="utf-8") as f:
            secret = f.read().strip()
            if varname:
                #varname = juststem(filename).upper()
                os.environ[varname] = secret
            return secret
    return None

def load_secrets():
    """
    load_secrets
    """
    for root, _, files in os.walk("/run/secrets/"):
        for file in files:
            varname = juststem(file).upper()
            load_secret(file, varname)
