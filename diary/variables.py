directories = '''\
 /home\n /admin/
 /console
 /activity/list
 /diary/list
 /graph
 /diary/logout
'''

cmd_list = '''\
Press HOME key or use commands below:
 dir - displays possible directories
 active users - displays all registered users with valid csrf token
 results --option - displays table with current results, where
    option have to be exactly one from list below
      --five - displays five best scores
      --ten - displays ten best scores
      --full - displays whole results
      --last - displays whole results from last action
 repair profiles - recount all points for users profiles
 repair weeks - recount points pertaining to all weeks from all users
 generate code - generate new approval code
 active codes - displays all active approval codes
 error list - displays all unsolved duplicate errors
 test - prints Hello world!
 help - displays this help message
 exit - flushs all your sessions for this website
'''
