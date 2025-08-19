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
        self.assertEq('data[*].showType', 2)

    # @kytest.title("form请求")
    # def test_form_req(self):
    #     url = '/qzd-bff-patent/image-search/images'
    #     m = MultipartEncoder(
    #         fields={
    #             # 'key1': 'value1',
    #             'imageFile': ('logo.png', open('data/logo.png', 'rb'), 'image/png')
    #         }
    #     )
    #     self.post(url, data=m, headers={'Content-Type': m.content_type})
    #     self.assertEq("code", 0)

