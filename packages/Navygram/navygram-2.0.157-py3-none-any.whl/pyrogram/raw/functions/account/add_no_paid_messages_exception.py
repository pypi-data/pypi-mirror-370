#  Pyrogram - Telegram MTProto API Client Library for Python
#  Copyright (C) 2017-present Dan <https://github.com/delivrance>
#
#  This file is part of Pyrogram.
#
#  Pyrogram is free software: you can redistribute it and/or modify
#  it under the terms of the GNU Lesser General Public License as published
#  by the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  Pyrogram is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU Lesser General Public License for more details.
#
#  You should have received a copy of the GNU Lesser General Public License
#  along with Pyrogram.  If not, see <http://www.gnu.org/licenses/>.

from io import BytesIO

from pyrogram.raw.core.primitives import Int, Long, Int128, Int256, Bool, Bytes, String, Double, Vector
from pyrogram.raw.core import TLObject
from pyrogram import raw
from typing import List, Optional, Any

# # # # # # # # # # # # # # # # # # # # # # # #
#               !!! WARNING !!!               #
#          This is a generated file!          #
# All changes made in this file will be lost! #
# # # # # # # # # # # # # # # # # # # # # # # #


class AddNoPaidMessagesException(TLObject):  # type: ignore
    """Telegram API function.

    Details:
        - Layer: ``201``
        - ID: ``6F688AA7``

    Parameters:
        user_id (:obj:`InputUser <pyrogram.raw.base.InputUser>`):
            N/A

        refund_charged (``bool``, *optional*):
            N/A

    Returns:
        ``bool``
    """

    __slots__: List[str] = ["user_id", "refund_charged"]

    ID = 0x6f688aa7
    QUALNAME = "functions.account.AddNoPaidMessagesException"

    def __init__(self, *, user_id: "raw.base.InputUser", refund_charged: Optional[bool] = None) -> None:
        self.user_id = user_id  # InputUser
        self.refund_charged = refund_charged  # flags.0?true

    @staticmethod
    def read(b: BytesIO, *args: Any) -> "AddNoPaidMessagesException":
        
        flags = Int.read(b)
        
        refund_charged = True if flags & (1 << 0) else False
        user_id = TLObject.read(b)
        
        return AddNoPaidMessagesException(user_id=user_id, refund_charged=refund_charged)

    def write(self, *args) -> bytes:
        b = BytesIO()
        b.write(Int(self.ID, False))

        flags = 0
        flags |= (1 << 0) if self.refund_charged else 0
        b.write(Int(flags))
        
        b.write(self.user_id.write())
        
        return b.getvalue()
