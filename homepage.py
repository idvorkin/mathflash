import hyperdiv as hd


def home():
    hd.markdown(
        """

# Welcome to math flash!

### Future features
* Eventually we'll have per user login,
    * Which will load settings and record answers to DB

### For now

* You need to pass the URL yourself
    * [/subtract/20](/subtract/20)
    * [/add/7](/subtract/7)
 """
    )
