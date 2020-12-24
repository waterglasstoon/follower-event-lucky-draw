# follower-event-lucky-draw

팔로워 이벤트용으로 만든 간단한 스크립트입니다. 본인의 특정 게시글에 댓글을 남긴 유저들을 뽑아와서 상품별로 추첨합니다. <br>

## Prerequisites
- python 3.6 이상 사용 (하시거나 f-string 문법을 고치시고 python 3점대를 사용해주세요)
- 해당 포스트의 인스타그램 계정과 연결된 facebook developer 계정
- ..을 통해서 가져온 본인의 access token과 post id

### Facebook Graph API
(Facebook graph API 사용하지 않고 코멘트 리스트 가져오는 방법은 Detail-1번에 있습니다)<br><br>
공식 API를 사용해서 특정 게시물의 코멘트를 가져오기 위해선 우선 아래와 같은 준비를 해야합니다.

1. https://developers.facebook.com/ 에 들어가서 개발자 계정 생성
2. 해당 계정을 인스타그램 계정이랑 연동 (계정의 페이스북 페이지와 연동)

위 과정을 마치면 https://developers.facebook.com/docs/instagram-api/getting-started
가이드를 따라 auth token과 포스트의 media id를 찾아낼 수 있습니다.

## Run
```shell
vi run.py # POST_ID, ACCESS_TOKEN 수정
python3 run.py
```

## Detail
해야 할 일은 크게 세가지로 나눠 볼 수 있습니다.
1. 해당 인스타그램 게시물의 댓글에서 유저 목록 추출 (대댓글 제외)
2. 유저 중 팔로워가 아닌 사람 제외
3. 유저 중에서 상품별 랜덤추첨

1번같은 경우 공식적으로 제공하는 graph API를 사용하는 방법과, 인스타그램에서 실제 서비스를 제공할때 사용하는 graphql쿼리를 뜯어서 사용하는 방법이 있습니다. 이번에는 첫번째 방식을 사용했습니다. <br>
첫번째 방식은 비교적 맘놓고 사용할 수 있긴 하지만 사용하기 위해선 준비해야 할게 많고, 제약사항이 많은 단점이 있습니다 (인스타 개인정보 정책이 바뀌면서 더 힘들어진 것 같습니다). <br>
두번 방식은 따로 세팅이 필요없고 제약사항도 비교적 적지만 추측해서 사용해야 하는 게 많고, 스크래핑하는 서비스를 쓰다가 계정이 막혀본적 있어서 좀 불안했습니다. <br>
각 방식에 대해서는 아래에 좀 더 자세히 설명하겠습니다. <br>

2번은 graph API만 사용해서는 힘들고, 스크래핑하면 되긴 하지만 앞에 말했듯이 계정이 막혀본적 있어서 좀 무서웠습니다. 그래서 그냥 추첨 후에 수동으로 확인하기로 했습니다. <br>
방식은 아래에 짧게 설명하겠습니다. <br>

3번에서는 특정 상품을 받고싶어하지 않는 분들을 필터링해서 추첨합니다. 중복 당첨은 없습니다. <br>

### 해당 인스타그램 게시물의 댓글에서 유저 목록 추출 (대댓글 제외)
#### Graph API 사용
먼저 https://developers.facebook.com/docs/instagram-api/getting-started 를 참고해서 auth 토큰과 포스트의 media id를 가져옵니다. <br>

다음으로 https://developers.facebook.com/docs/instagram-api/reference/media/comments/ 을 참고해서 해당 포스트의 코멘트를 가져옵니다.
한번에 가져올 수 있는 개수는 현재 50개 이하인 것 같고, 그 다음 목록은 paging.next를 사용해서 가져옵니다. <br>
run.py의 get_comment_users를 참고하세요.

#### graphql 사용
웹에서 인스타그램에 로그인하고 본인 포스트를 눌러주세요. 개발자 도구를 켜주시고 network 탭에 들어간 상태로 리프레시를 한번 해주세요. <br>
이상태에서 Name 탭을 한번 눌러서 정렬을 해주시면 "?query_hash=..."로 시작하는 graphql 쿼리들이 보입니다. <br>
이중에서 코멘트를 받아오는 리퀘스트를 찾아주세요(또는 댓글 더보기를 눌렀을때 들어오는 "?query_hash=..." 리퀘스트를 클릭해주세요) <br>
url의 모양은 이렇습니다:
```html
https://www.instagram.com/graphql/query/?query_hash=<query_hash>&variables={"shortcode":"...","first":<count>,"after":"<cursor>"}
```
여기서 first는 개수제한으로 테스트해봤을때 위와 동일하게 50개가 최대인 것 같습니다. after는 paging 파라미터입니다. <br>

body의 모양은 이렇습니다:
```json
{
   "data": {
       "shortcode_media": {
           "edge_media_to_parent_comment": {
               "count": 100,
               "edges": [{
                   "node": {
                       "owner": {
                           "id": "<owner_id>",
                           "username": "<username>"
                        }
                   }
               }],
               "page_info": {
                   "has_next_page": true,
                   "end_cursor": "<end_cursor>"
               }
           }
}}}
```
여기서 page_info.end_cursor가 url의 after에 들어가게 되면 그 이후 포스트를 가져오게 됩니다. <br>

### 유저 중 팔로워가 아닌 사람 제외
추첨 후에 수동으로 확인하기로 했지만, 가져오는 방법은 간단히 정리합니다.<br>
https://www.instagram.com/<username>/?__a=1를 호출하면 다음과 같은 응답이 내려옵니다:
```json
{
  "graphql": {
    "user": {
      "follows_viewer": false
    }
  }
}
```
follows_viewer 필드로 본인을 팔로우하는지 확인할 수 있습니다.
