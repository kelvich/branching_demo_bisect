# Neon branch bisect demo

Imagine you've accidentally deleted some important data from your table now you want to reset your database to the point in time right before that deletion. To do that you need to know the exact lsn or time of the event. Since we can create branches from the past we can easily find that using binary search on lsn.

Let's say we accidentally deleted a user named neon from the table called users. To find when that happened we can create branches in past and check whether `select exists(select name from users where name='neon')` is true or not. Using binary search that process quickly converges.

To run this script one will need Neon API Key `$NEON_API_KEY` and database password `$PGPASSWORD`:

```
> export NEON_API_KEY=<...>
> export PGPASSWORD=<...>
> python3 bsearch_neon.py

Main branch id is: "br-rough-queen-879713
Creating branch at lsn = 0/1628D2B4
Checking "select exists(select name from users where name='neon')" at lsn "0/1628D2B4": -> True
Creating branch at lsn = 0/1A6405E6
Checking "select exists(select name from users where name='neon')" at lsn "0/1A6405E6": -> False
Creating branch at lsn = 0/18466C4D
<...>
Creating branch at lsn = 0/16924A8A
Checking "select exists(select name from users where name='neon')" at lsn "0/16924A8A": -> False
Creating branch at lsn = 0/16924A88
Checking "select exists(select name from users where name='neon')" at lsn "0/16924A88": -> True
Creating branch at lsn = 0/16924A89
Checking "select exists(select name from users where name='neon')" at lsn "0/16924A89": -> False
Converged at 0/16924A89
Finishing
```
