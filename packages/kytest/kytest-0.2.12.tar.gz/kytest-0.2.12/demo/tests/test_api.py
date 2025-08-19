"""
@Author: kang.yang
@Date: 2023/11/16 17:52
"""
import kytest
from requests_toolbelt import MultipartEncoder


@kytest.story('pc首页')
class TestApiDemo(kytest.TC):

    @kytest.title('get/post请求')
    @kytest.data('body', [{"type": 1}, {"type": 2}])
    def test_normal_req(self, body):
        url = '/qzd-bff-app/qzd/v1/home/getToolCardListForPc'
        self.post(url, json=body)
        self.assertEqual('data[0].showType', 2)

    @kytest.title("form请求")
    def test_form_req(self):
        url = '/qzd-bff-patent/image-search/images'
        fields = {
            'imageFile': ('logo.png', open('data/logo.png', 'rb'), 'image/png')
        }
        form_data = MultipartEncoder(fields=fields)
        headers = {'Content-Type': form_data.content_type}
        self.post(url, data=form_data, headers=headers)
        self.assertEqual("code", 0)


