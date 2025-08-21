from .logic import parse_kintone_url
from .dto import KintoneUrl
from .dto import KintoneSpaceUrl
from .dto import KintoneThreadUrl
from .dto import KintonePeopleUrl
from .dto import KintoneMessageUrl
from .dto import KintoneCommentUrl
from .dto import KintoneChildCommentUrl
from .dto import KintoneThreadCommentUrl
from .dto import KintoneThreadChildCommentUrl
from .dto import KintonePeopleCommentUrl
from .dto import KintonePeopleChildCommentUrl
from .dto import KintoneMessageCommentUrl
from .dto import KintoneAppUrl
from .dto import KintoneRecordUrl
from .dto import KintoneRecordCommentUrl
from .dto import KintoneNotifyUrl


__all__: list[str] = [
    parse_kintone_url.__name__,
    KintoneUrl.__name__,
    KintoneSpaceUrl.__name__,
    KintoneThreadUrl.__name__,
    KintonePeopleUrl.__name__,
    KintoneMessageUrl.__name__,
    KintoneCommentUrl.__name__,
    KintoneChildCommentUrl.__name__,
    KintoneThreadCommentUrl.__name__,
    KintoneThreadChildCommentUrl.__name__,
    KintonePeopleCommentUrl.__name__,
    KintonePeopleChildCommentUrl.__name__,
    KintoneMessageCommentUrl.__name__,
    KintoneAppUrl.__name__,
    KintoneRecordUrl.__name__,
    KintoneRecordCommentUrl.__name__,
    KintoneNotifyUrl.__name__
]
