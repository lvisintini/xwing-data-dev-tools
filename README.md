# X-Wing Data dev tools

These are just a collection of tools that I'm using to improve and normalize the data in:

- https://github.com/lvisintini/xwing-data
- https://github.com/guidokessels/xwing-data


The code here is not production ready, in the sense that I would never put this in a server or rely on it to make money.
However, if you feel like helping out in any of the above repos, you may find some the functions in here useful.

If you want to use this package, I would suggest the following setup:

```
$ git clone git@github.com:lvisintini/xwing-data-dev-tools.git
$ mkvirtualenv --python=`which python3` xwing-data-dev-tools
$ python setup.py develop
```

After that, just make the adjustments you want and run the scripts directly from the checked out folder.
