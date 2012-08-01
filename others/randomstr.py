#!/usr/bin/env/python
# coding: utf-8
import sys
import os
reload(sys)
sys.setdefaultencoding(sys.getfilesystemencoding())
characters = [x for x in raw_input(u'请输入生成随机字符串时允许出现的字符：')]
if '\n' in characters:
    characters = characters.remove('\n')
if '\r' in characters:
    characters = characters.remove('\r')
characters = {}.fromkeys(characters).keys()
print >>sys.stderr, u'字符集中一共有：%d个字符' % (len(characters))
length = input(u'请输入生成随机字符串的长度：')
assert(type(length) == int or type(length) == long)
total_count = input(u'请输入生成随机字符串数量：')
assert(type(total_count) == int or type(total_count) == long)
assert(total_count > 0)
partition = input(u'请输入插入分隔符的间隔（系统会每隔这么多字插入一个分隔符），0表示不插入分隔符：')
assert(type(partition) == int or type(partition) == long)
assert(partition >= 0)
if partition > 0:
    seperator = raw_input(u'请输入分隔符（只能有一个字符）：')[0]
else:
    seperator = ''
print >>sys.stderr, u'你输入的分隔符是：%s' % seperator
if seperator in characters:
    print >>sys.stderr, u'警告：你输入的分隔符在你输入的字符集中！！'
print >>sys.stderr, u'请选择随机数源'
print >>sys.stderr, u'\t1. 数学上的伪随机，使用当前时间距离格林威治时间1970年1月1日00:00:00的秒数作为种子。'
print >>sys.stderr, u'\t2. 系统随机数，来源与/dev/urandom （Unix） 或 CryptGenRandom （Windows）。不是所有操作系统都能使用。'
print >>sys.stderr, u'\t3. Random.org 空气布朗运动观测数据。使用该数据源需要互联网连接。 Random.org对每个IP提供的随机数长度有限，除非你购买其服务。'
print >>sys.stderr, u'\t4. 澳大利亚国立大学量子计算与通信中心量子随机数生成器。使用该数据源需要互联网连接。'
random_source = input(u'请选择，输入选项前面的数字：')
assert(random_source in [1,2,3, 4])
generator = None
if random_source == 1:
    import random, time
    generator = random.Random(x = long(time.time()))
elif random_source == 2:
    import random
    generator = random.SystemRandom()
elif random_source == 3:
    class RandomOrgRandom():
        def __init__(self):
            pass
        def randint(self, a, b):
            #http://www.random.org/integers/?num=10&min=1&max=6&col=1&base=10&format=plain&rnd=new
            import urllib2
            number = int(urllib2.urlopen('http://www.random.org/integers/?num=1&min=%d&max=%d&col=1&base=10&format=plain&rnd=new' % (a, b)).read())
            return number
        def choice(self, seq):
            return seq[self.randint(0, len(seq) - 1)]
    generator = RandomOrgRandom()
elif random_source == 4:
    class ANURandom():
        def __init__(self):
            pass
        def randint(self, a, b):
            #http://qrng.anu.edu.au/form_handler.php?numofsets=1&min_num=0&max_num=5&repeats=yes
            import urllib2, re
            s = urllib2.urlopen('http://qrng.anu.edu.au/form_handler.php?numofsets=1&min_num=%d&max_num=%d&repeats=yes' % (a, b)).read()
            n = int(re.match('Random permutations with repetitions<br/>Your random numbers are: <br />([0-9]*)<br />',  s).group(1))
            return n
        def choice(self, seq):
            return seq[self.randint(0, len(seq) - 1)]
    generator = ANURandom()


save_file = input(u'是否同时保存到文件？（1 = 是， 0 = 否） ')
assert(save_file in [0, 1])
if save_file == 1:
    filename = raw_input(u'请输入文件路径（包括目录和文件名）：')
    while filename[-1] == '\n' or filename[-1] == '\r':
        filename = filename[0:-1]

if save_file == 1:
    f = open(filename, 'w')

import time


def duration_to_str(duration):
    s = ''
    if duration == 0:
        return '0秒'
    if duration >= 3600:
        s += '%d小时' % (duration / 3600)
        duration /= 3600
    if duration > 60:
        s += '%d分' % (duration / 60)
        duration %= 60
    if duration > 0:
        s += '%d秒' % (duration)
    return s



total_capacity = total_count * length
begin = last = time.time()


for i in xrange(total_count):
    s = ''
    for j in xrange(length):
        if time.time() - last > 10:
            cpac = i * length + j
            freetime = (total_capacity - cpac) * 1.0 / cpac * (time.time() - begin)
            print >>sys.stderr, u'进度：%0.2lf%%，预计剩余时间：%s' % (cpac * 100.0 / total_capacity, duration_to_str(freetime))
            last = time.time()
        s += generator.choice(characters)
        if partition > 0 and (j % partition == partition - 1) and j != length - 1:
            s += seperator
    print s
    if save_file == 1:
        f.write(s +  os.linesep)

if save_file == 1:
    f.close()

raw_input(u'所有随机字符串已生成完毕。')
