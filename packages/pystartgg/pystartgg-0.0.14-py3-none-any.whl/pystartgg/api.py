import time
import requests
from pystartgg.exceptions import *

# Runs queries
def run_query(query, variables, header, auto_retry):
    # This helper function is necessary for TooManyRequestsErrors
    def _run_query(query, variables, header, auto_retry):
        json_request = {'query': query, 'variables': variables}
        try:
            request = requests.post(url='https://api.start.gg/gql/alpha', json=json_request, headers=header)
            if request.status_code == 400:
                raise RequestError
            elif request.status_code == 429:
                raise TooManyRequestsError
            elif 400 <= request.status_code < 500:
                raise ResponseError
            elif 500 <= request.status_code < 600:
                raise ServerError
            elif 300 <= request.status_code < 400:
                raise NoIdeaError

            response = request.json()
            if 'errors' in response:
                raise ResponseError(response['errors'][0]['message'])
            return response

        except TooManyRequestsError as err:
            if auto_retry == 0:
                raise err
            else:
                print("Error 429: Sending too many requests right now. Auto-retry in {} seconds".format(auto_retry))
                time.sleep(auto_retry)
                return _run_query(query, variables, header, auto_retry*2)

        # except RequestError:
        #     print("Error 400: Bad request (probably means your key is wrong)")
        #     return
        # except ResponseError:
        #     print("Error {}: Unknown request error".format(request.status_code))
        #     return
        # except ServerError:
        #     print("Error {}: Unknown server error".format(request.status_code))
        #     return
        # except NoIdeaError:
        #     print("Error {}: I literally have no idea how you got this status code, please send this to me".format(request.status_code))
        #     return

    return _run_query(query, variables, header, auto_retry)

def paginated(func, multi_return = False):
    def looper(*args, **kwargs):
        page_num = 1
        retry_limit = 5
        results = []
        try_count = 0
        while True:
            kwargs['page_num'] = page_num
            try:
                curr = func(*args, **kwargs)
                if not multi_return:
                    curr = [curr]

                if curr[0] is None:
                    break
                if not curr[0]:
                    break

                if results == []:
                    results = curr
                else:
                    for i, c in enumerate(curr):
                        results[i].extend(c)

                page_num += 1
                try_count = 0

            except TypeError:
                try_count += 1
                if try_count >= retry_limit:
                    raise TypeError(
                        'Retry limit exceeded for API call: {}({}, {})'.format(
                            func.__name__, args, kwargs
                        )
                    )
        if multi_return:
            return results
        else:
            if results == []:
                return None
            return results[0]

    return looper