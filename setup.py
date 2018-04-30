from setuptools import setup


setup(name='dshell', version='1.02', description='Dolphin Shell for Acoustic Modem',
	url='http://github.com/delresearch/dshell', author='delResearch LLC.', author_email='info@delresearch.com',
	license='MIT', packages=['dshell'], install_requires=['cmd2'],
	scripts=['bin/dshell'], zip_safe=False)

