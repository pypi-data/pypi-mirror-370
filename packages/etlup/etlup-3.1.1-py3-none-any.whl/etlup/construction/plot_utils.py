
from io import BytesIO
import base64

def convert_fig_to_html_img(fig) -> str:
    buf = BytesIO()
    fig.savefig(buf, format="png", bbox_inches='tight')
    # Embed the result in the html output.
    data = base64.b64encode(buf.getbuffer()).decode("ascii")
    # style = "width: 80%; height: auto; @media only screen and (max-width: 390px) { img {width: 100px;} }"
    # return f"<img src='data:image/png;base64,{data}' style={style}>"
    img = f'<img src="data:image/png;base64,{data}" style="width: clamp(300px, 75vw, 1000px); height: auto;">'
    return img