## vim Tips
### 1 move
ctr+o / ctr+i : 跳转到上/下一次
ctr+]         : 进入函数

## latex
### 1 特殊符号
[箭头](https://devdocs.io/latex/arrows)<br>
$\leftarrow$
$\Longleftarrow$

梯度：$\nabla$

冒号: $f\colon D\to C$

偏导：$\partial$

省略号：$\cdots$

单个为$\cdot$

手写体：$\mathcal{handscript}$

粗体：$\bold{asdf}$

数学空心：$\mathbb{E}$

空集：$\varnothing$

### 2 数学
```latex
$$
\frac{numerator}{denominator}
\} or \rbrace or \lbrack or \lfloor or \lceil or \backslash or \|
$$
$$
\begin{array}{cccc}
  a_{0,0}    &a_{0,1}   &a_{0,2} &\   \ldots \\
  a_{1,0}    &\ddots                     \\
  \vdots
\end{array}
$$
$$
  \frac{\partial^2u}{\partial t^2} = c^2\nabla^2u
$$
```
## net tools

### 1 网口查看
- 1 windows: netstat -ano


## standards/styles

### 0.1 restful风格 [https://www.cnblogs.com/MTRD/p/12153561.html](https://www.cnblogs.com/MTRD/p/12153561.html)
### 0.2 url规范 [https://www.cnblogs.com/hduwbf/p/7300794.html](https://www.cnblogs.com/hduwbf/p/7300794.html)
### 0.3 sprint boot处理各种需求[https://spring.io/guides](https://spring.io/guides)

## 2020/10/09
替换windows路径
```sh
sed -i 's|\\|/|g' ./result.txt
sed -i 's|D:/Datasets/guangtie/LessImages/dense|/home/ld/Documents/modelFiles/123/mvs|g' ./result.txt
```

## 2020/10/11

### 1 使用OpenMVS贴纹理
#### 1.1 文件准备
the dir which has result.out(camera's info), should have a result.txt which demostrate where is the images
attention: result.txt should be the imagelist file;
```sh
[nash5 mvs]# head -n 5 result.txt 
/home/ld/Documents/modelFiles/123/mvs/images/DJI_0146.JPG
/home/ld/Documents/modelFiles/123/mvs/images/DJI_0132.JPG
/home/ld/Documents/modelFiles/123/mvs/images/DJI_0133.JPG
/home/ld/Documents/modelFiles/123/mvs/images/DJI_0134.JPG
/home/ld/Documents/modelFiles/123/mvs/images/DJI_0141.JPG
[nash5 mvs]# head -n 10 result.out
# Bundle file v0.3
63 66674
4318.92 0 0
-0.999016 0.0442186 0.003457
0.0197872 0.514087 -0.85751
-0.0396951 -0.856598 -0.514456
-0.285562 3.57279 -1.96389
4318.92 0 0
-0.999732 0.00834863 0.0216004
-0.0141811 0.5167 -0.856049
```
#### 1.2 使用OpenMVS转换文件格式然后贴纹理
```sh
/home/ld/prjs/OpenMVS/openMVS_build/bin/InterfaceVisualSFM -i result.out -o new
/home/ld/prjs/OpenMVS/openMVS_build/bin/TextureMesh --mesh-file ./result_dense_mesh_refined.ply -i new.mvs -o textured
```

### 2 使用MVE和texRecon贴纹理
#### 2.0 MVE和texRecon安装
[https://www.gcc.tu-darmstadt.de/home/proj/texrecon/index.en.jsp](https://www.gcc.tu-darmstadt.de/home/proj/texrecon/index.en.jsp)
在使用texRecon的时候, 注意如下:
texrecon/elibs/mve/libs/mve/camera.cc +125的
<font color=#FF0000> void CameraInfo::fill_calibration </font>函数

其ax乘的flen是单位化以后的flen， 单位化的flen的方式见[https://github.com/simonfuhrmann/mve/wiki/Math-Cookbook](https://github.com/simonfuhrmann/mve/wiki/Math-Cookbook): 
```cpp
void
CameraInfo::fill_calibration (float* mat, float width, float height) const
{
    float dim_aspect = width / height;
    float image_aspect = dim_aspect * this->paspect;
    float ax, ay;
    if (image_aspect < 1.0f) /* Portrait. */
    {
        ax = this->flen * height / this->paspect;
        ay = this->flen * height;
    }
    else /* Landscape. */
    {
        ax = this->flen * width;
        ay = this->flen * width * this->paspect;
    }
    mat[0] = this->flen; mat[1] =       0.0f; mat[2] =  width * this->ppoint[0];
    mat[3] =       0.0f; mat[4] = this->flen; mat[5] = height * this->ppoint[1];
    mat[6] =       0.0f; mat[7] =       0.0f; mat[8] =                     1.0f;
    //mat[0] =   ax; mat[1] = 0.0f; mat[2] = width * this->ppoint[0];
    //mat[3] = 0.0f; mat[4] =   ay; mat[5] = height * this->ppoint[1];
    //mat[6] = 0.0f; mat[7] = 0.0f; mat[8] = 1.0f;
}
```

#### 2.1 对相机数据进行预处理然后转化格式
- 1 你会发现相机的平移和旋转矩阵的后两行都添加了负号(使用meshlab打开看相机的朝向和result.out的rot[2][2] (代表相机朝向的是z正方向还是负方向))， 按照需要改过来并且转换为MVE支持的一种格式(详细见2.2),该bundle file的详细格式可以参考：[https://www.cs.cornell.edu/~snavely/bundler/bundler-v0.4-manual.html](https://www.cs.cornell.edu/~snavely/bundler/bundler-v0.4-manual.html)
```sh
### ori camfile from colmap:
[nash5 123]# head -n 10 result.out 
# Bundle file v0.3
63 66674                        # imageNum pointsNum
4318.92 0 0                     # focal_len disortionCoe1 distortionCoe2
-0.999732 0.00834863 0.0216004  # rot[0][0:2]
-0.0141811 0.5167 -0.856049     # rot[1][0:2]
-0.0183078 -0.856126 -0.516443  # rot[2][0:2]
1.99173 4.31377 -2.39484        # translation[0:2]
4318.92 0 0
-0.999016 0.0442186 0.003457
0.0197872 0.514087 -0.85751
### 转换后（针对于一个数据）
[nash5 123]# cd scene1006/
[nash5 scene1006]# cat DJI_0132.CAM 
1.99173 -4.31377 2.39484 -0.999732 0.00834863 0.0216004 .0141811 -.5167 .856049 .0183078 .856126 .516443
4318.92 0 0 1 0.5 0.5
```
#### 2.2 文件格式准备:
首先需要有4个文件：
```sh
result_dense_mesh_refined.ply # 需要贴图的mesh
result.imagelist              # 贴图的图片的位置（views）
result.out                    # 每个图片（view）的相机参数
images/*.JPG                  # 图片
[nash5 123]# head -n 5 result.imagelist
/home/ld/Documents/modelFiles/123/mvs/images/DJI_0146.JPG
/home/ld/Documents/modelFiles/123/mvs/images/DJI_0132.JPG
/home/ld/Documents/modelFiles/123/mvs/images/DJI_0133.JPG
/home/ld/Documents/modelFiles/123/mvs/images/DJI_0134.JPG
/home/ld/Documents/modelFiles/123/mvs/images/DJI_0141.JPG
```
- 1 转化后的数据(转化要求详见: texRecon -h或mve在github上的math部分)例子：使用脚本将result.out作为输入, 为每一个图片生成一个.CAM文件：(可以参照：[https://github.com/xychen5/fft/blob/master/colmapToTexrecon/turnYZ_in_camera_rot_and_translation.sh](https://github.com/xychen5/fft/blob/master/colmapToTexrecon/turnYZ_in_camera_rot_and_translation.sh))
```sh
### 转换前（使用texrecon -h获得它需要的文件格式）
[nash5 123]# head -n 10 result.out 
# Bundle file v0.3
63 66674                        # imageNum pointsNum
4318.92 0 0                     # focal_len disortionCoe1 distortionCoe2
-0.999732 0.00834863 0.0216004  # rot[0][0:2]
-0.0141811 0.5167 -0.856049     # rot[1][0:2]
-0.0183078 -0.856126 -0.516443  # rot[2][0:2]
1.99173 4.31377 -2.39484        # translation[0:2]
4318.92 0 0
-0.999016 0.0442186 0.003457
0.0197872 0.514087 -0.85751
### 转换后（针对于一个数据）
[nash5 123]# cd scene1006/
[nash5 scene1006]# cat DJI_0132.CAM 
1.99173 -4.31377 2.39484 -0.999732 0.00834863 0.0216004 .0141811 -.5167 .856049 .0183078 .856126 .516443
4318.92 0 0 1 0.5 0.5
```
- 2 经过step1获得如下一个文件夹：（对应的每一个图片都有一个相机文件）
```sh
[nash5 reRun]# ls scene1006/
 DJI_0132.CAM   DJI_0145.CAM   DJI_0188.CAM      'DJI_0303(1).CAM'   DJI_0327.CAM   DJI_0334.CAM   DJI_0341.CAM   DJI_0348.CAM   DJI_0367.CAM
 DJI_0132.JPG   DJI_0145.JPG   DJI_0188.JPG      'DJI_0303(1).JPG'   DJI_0327.JPG   DJI_0334.JPG   DJI_0341.JPG   DJI_0348.JPG   DJI_0367.JPG
```
- 3 将该文件夹作为texRecon的输入即可：(耗时较长，几十分钟到几个小时，看数据和机器)
```sh
/home/ld/prjs/recon3d/texRecon/texrecon/cmake-build-debug/apps/texrecon/texrecon scene1006 result_dense_mesh_refined.ply textured2 --skip_geometric_visibility_test
```

## 2020/10/13
margin probality

## 2020/10/19
- 3 注释补齐插件 for vim
- 2 BP算法详细博文
- 1 导出osgb然后查看

bug:       关注读取图片后，m_image_data结构体的值: 在出入函数前后，本来被修改的图片的宽高数据在出函数后却是0。
fix:          因为真实的处理逻辑确实如此，主要是因为在快出函数的时候有一个函数又将宽高数据更改成0了。
suggest: debug的时候一定每一个流程都要认真看，尤其是经过了函数，务必进入，然后就是少用debugger（只定位问题），直接看代码效率高。

## 2020/10/24
pac __SuiteSparse__. Needed for solving large sparse linear systems. Optional; strongly recomended for large scale bundle adjustment
pac __TBB__ is a C++11 template library for parallel programming that optionally can be used as an alternative to OpenMP. Optional

CGAL的依赖很多，QT在E:/360Downloads里面有

## 2020/10/25

### 安装GMP和MFPR
- 1 安装Cygwin
```log
Setup Environment
Install Cygwin, add the following packages to the default installation
gcc-core
gcc-g++
libgcc
m4
make #不知为何安装后在Cygwin根目录下搜不到make程序
cmake
bash
Add the following Environment Variable to the User PATH: C:\Program Files (x86)\Microsoft Visual Studio\2017\Enterprise\VC\Tools\MSVC\14.15.26726\bin\Hostx64\x64
This is so you can use the lib command. Your lib.exe may be located elsewhere.
```
安装好Cygwin以及一些依赖以后，在其根目录(方便说明记为： CygwinRoot="D:\CygwinRooto")下的bin/minnty.exe是其终端入口，然后每次打开该终端，进入的是：$CygwinRoot/home/$(userName)， 运行"cd /"后就可以理解了； 

- 2 下载并安装make
  - 2.1 从如下网址下载make的源码，https://ftp.gnu.org/gnu/make/，然后解压
  - 2.2 打开Cygwin64 Terminal命令行，进入源码根目录，然后运行：configure && ./build.sh
  - 2.3 编译得到了make.exe后将其移动到Cygwin的bin目录下

- 3 编译gmp
运行两个： ./configure 和 make install
```sh
./configure --prefix=/home/chenxy/mylibs/newTry/gmp-6.2.0/build/static --enable-static --disable-shared
configure: summary of build options:
  Version:           GNU MP 6.2.0
  Host type:         skylake-pc-cygwin
  ABI:               64
  Install prefix:    /home/chenxy/mylibs/newTry/gmp-6.2.0/build/static
  Compiler:          gcc
  Static libraries:  yes
  Shared libraries:  no
```
编译结果（默认生成的是static的数据）：
```log
@nash-5 ~/mylibs/gmp-6.2.0
$ ls /usr/local/include/
gmp.h
@nash-5 ~/mylibs/gmp-6.2.0
$ ls /usr/local/lib/
libgmp.a  libgmp.la  pkgconfig
```
生成动态连接库（注意： 动态连接库和静态连接库的.h文件不同，所以注意分成2个文件夹，至少对于gmp是如此）：
```sh
./configure --prefix=/home/chenxy/mylibs/gmp-6.2.0/build/shared --enable-shared --disable-static
```
- 4 编译mfpr（需要gmp的依赖，而且是动态连接库）
进入mfpr的根目录：
运行./configure：
```log
checking for gmp.h... no
configure: error: gmp.h can't be found, or is unusable.
```
运行./configure --help
```sh
···
  --with-gmp-include=DIR  GMP include directory
  --with-gmp-lib=DIR      GMP lib directory
···
```
所以：
```sh
./configure --prefix=/home/chenxy/mylibs/newTry/mpfr-4.1.0/build/static \
--enable-static --disable-shared \
--with-gmp-include=/home/chenxy/mylibs/newTry/gmp-6.2.0/build/static/include \
--with-gmp-lib=/home/chenxy/mylibs/newTry/gmp-6.2.0/build/staic/lib
make install
```
```sh
./configure --prefix=/home/chenxy/mylibs/mpfr-4.1.0/build/static \
--with-gmp-include=/home/chenxy/mylibs/gmp-6.2.0/build/static/include \
--with-gmp-lib=/home/chenxy/mylibs/gmp-6.2.0/build/static/lib \
--enable-static --disable-shared
```

### cmake查看debug信息辅助cmake配置
以boost错误为例：
在（cmake-gui中）配置了变量：Boost_INCLUDE_DIR=Z:/BASE_ENV/forOpenMVS/boost_1_74_0后依然出错
```log
CMake Error at Z:/BASE_ENV/CMake/share/cmake-3.18/Modules/FindPackageHandleStandardArgs.cmake:165 (message):
  Could NOT find Boost (missing: Boost_INCLUDE_DIR iostreams program_options
  system serialization)
Call Stack (most recent call first):
  Z:/BASE_ENV/CMake/share/cmake-3.18/Modules/FindPackageHandleStandardArgs.cmake:458 (_FPHSA_FAILURE_MESSAGE)
  Z:/BASE_ENV/CMake/share/cmake-3.18/Modules/FindBoost.cmake:2177 (find_package_handle_standard_args)
  CMakeLists.txt:122 (FIND_PACKAGE)
```
则提供解决bug的思路：
- 1 首先，到cmake的安装目录里查看文件： _CMake/share/cmake-3.18/Modules/FindBoost.cmake_， 其定义了Boost的各个参数分别代表什么意思： 根据每个变量对应的实际意义重新配置一下即可；例如boost，主要配置两个参数： 
>  - Boost_INCLUDE_DIR: 含有boost头文件的目录
>  - Boost_LIBRARYDIR: 偏好的含有boost库的库目录
- 2 若配置完仍然有问题，可以根据 _CMake/share/cmake-3.18/Modules/FindBoost.cmake_ 文件里规定的debug参数： Boost_DEBUG=ON(在cmake-gui中则是添加一个entery，然后其bool值为true即可，直接在CMakeLists.txt里，则是添加： set(Boost_DEBUG ON) 就会打开调试信息)，根据调试信息再去对比生成的库的文件名称和搜索目录等信息，如下给出样例的调试信息：
```log
[ Z:/BASE_ENV/CMake/share/cmake-3.18/Modules/FindBoost.cmake:1491 ] _boost_TEST_VERSIONS = "1.73.0;1.73;1.72.0;1.72;1.71.0;1.71;1.70.0;1.70;1.69.0;1.69;1.68.0;1.68;1.67.0;1.67;1.66.0;1.66;1.65.1;1.65.0;1.65;1.64.0;1.64;1.63.0;1.63;1.62.0;1.62;1.61.0;1.61;1.60.0;1.60;1.59.0;1.59;1.58.0;1.58;1.57.0;1.57;1.56.0;1.56;1.55.0;1.55;1.54.0;1.54;1.53.0;1.53;1.52.0;1.52;1.51.0;1.51;1.50.0;1.50;1.49.0;1.49;1.48.0;1.48;1.47.0;1.47;1.46.1;1.46.0;1.46;1.45.0;1.45;1.44.0;1.44;1.43.0;1.43;1.42.0;1.42;1.41.0;1.41;1.40.0;1.40;1.39.0;1.39;1.38.0;1.38;1.37.0;1.37;1.36.1;1.36.0;1.36;1.35.1;1.35.0;1.35;1.34.1;1.34.0;1.34;1.33.1;1.33.0;1.33"
<被作者省略>
boost_1_74_0/../lib64-msvc-14.0;Z:/BASE_ENV/forOpenMVS/boost/lib64-msvc-14.0;PATHS;C:/boost/lib;C:/boost;/sw/local/lib"
[ Z:/BASE_ENV/CMake/share/cmake-3.18/Modules/FindBoost.cmake:1871 ] _boost_LIBRARY_SEARCH_DIRS_DEBUG = "Z:/BASE_ENV/forOpenMVS/boost_1_74_0/lib;Z:/BASE_ENV/forOpenMVS/boost_1_74_0/../lib;Z:/BASE_ENV/forOpenMVS/boost_1_74_0/stage/lib;Z:/BASE_ENV/forOpenMVS/boost_1_74_0/../lib64-msvc-14.1;Z:/BASE_ENV/forOpenMVS/local/lib"
<被作者省略>
CMake Warning at Z:/BASE_ENV/CMake/share/cmake-3.18/Modules/FindBoost.cmake:1187 (message):
  New Boost version may have incorrect or missing dependencies and imported
  targets
Call Stack (most recent call first):
  Z:/BASE_ENV/CMake/share/cmake-3.18/Modules/FindBoost.cmake:1311 (_Boost_COMPONENT_DEPENDENCIES)
  Z:/BASE_ENV/CMake/share/cmake-3.18/Modules/FindBoost.cmake:1919 (_Boost_MISSING_DEPENDENCIES)
  CMakeLists.txt:122 (FIND_PACKAGE)
CMake Warning at Z:/BASE_ENV/CMake/share/cmake-3.18/Modules/FindBoost.cmake:1187 (message):
  New Boost version may have incorrect or missing dependencies and imported
  targets
Call Stack (most recent call first):
  Z:/BASE_ENV/CMake/share/cmake-3.18/Modules/FindBoost.cmake:1311 (_Boost_COMPONENT_DEPENDENCIES)
  Z:/BASE_ENV/CMake/share/cmake-3.18/Modules/FindBoost.cmake:1919 (_Boost_MISSING_DEPENDENCIES)
  CMakeLists.txt:122 (FIND_PACKAGE)
CMake Warning at Z:/BASE_ENV/CMake/share/cmake-3.18/Modules/FindBoost.cmake:1187 (message):
  New Boost version may have incorrect or missing dependencies and imported
  targets
Call Stack (most recent call first):
  Z:/BASE_ENV/CMake/share/cmake-3.18/Modules/FindBoost.cmake:1311 (_Boost_COMPONENT_DEPENDENCIES)
  Z:/BASE_ENV/CMake/share/cmake-3.18/Modules/FindBoost.cmake:1919 (_Boost_MISSING_DEPENDENCIES)
  CMakeLists.txt:122 (FIND_PACKAGE)
CMake Warning at Z:/BASE_ENV/CMake/share/cmake-3.18/Modules/FindBoost.cmake:1187 (message):
  New Boost version may have incorrect or missing dependencies and imported
  targets
Call Stack (most recent call first):
  Z:/BASE_ENV/CMake/share/cmake-3.18/Modules/FindBoost.cmake:1311 (_Boost_COMPONENT_DEPENDENCIES)
  Z:/BASE_ENV/CMake/share/cmake-3.18/Modules/FindBoost.cmake:1919 (_Boost_MISSING_DEPENDENCIES)
  CMakeLists.txt:122 (FIND_PACKAGE)
CMake Warning at Z:/BASE_ENV/CMake/share/cmake-3.18/Modules/FindBoost.cmake:1187 (message):
  New Boost version may have incorrect or missing dependencies and imported
  targets
Call Stack (most recent call first):
  Z:/BASE_ENV/CMake/share/cmake-3.18/Modules/FindBoost.cmake:1311 (_Boost_COMPONENT_DEPENDENCIES)
  Z:/BASE_ENV/CMake/share/cmake-3.18/Modules/FindBoost.cmake:1919 (_Boost_MISSING_DEPENDENCIES)
  CMakeLists.txt:122 (FIND_PACKAGE)
[ Z:/BASE_ENV/CMake/share/cmake-3.18/Modules/FindBoost.cmake:2056 ] Searching for IOSTREAMS_LIBRARY_RELEASE: boost_iostreams-vc141-mt-x64-1_74;boost_iostreams-vc141-mt-x64;boost_iostreams-vc141-mt;boost_iostreams-vc140-mt-x64-1_74;boost_iostreams-vc140-mt-x64;boost_iostreams-vc140-mt;boost_iostreams-mt-x64-1_74;boost_iostreams-mt-x64;boost_iostreams-mt;boost_iostreams-mt;boost_iostreams
[ Z:/BASE_ENV/CMake/share/cmake-3.18/Modules/FindBoost.cmake:2111 ] Searching for IOSTREAMS_LIBRARY_DEBUG: boost_iostreams-vc141-mt-gd-x64-1_74;boost_iostreams-vc141-mt-gd-x64;boost_iostreams-vc141-mt-gd;boost_iostreams-vc140-mt-gd-x64-1_74;boost_iostreams-vc140-mt-gd-x64;boost_iostreams-vc140-mt-gd;boost_iostreams-mt-gd-x64-1_74;boost_iostreams-mt-gd-x64;boost_iostreams-mt-gd;boost_iostreams-mt;boost_iostreams
[ Z:/BASE_ENV/CMake/share/cmake-3.18/Modules/FindBoost.cmake:2056 ] Searching for PROGRAM_OPTIONS_LIBRARY_RELEASE: boost_program_options-vc141-mt-x64-1_74;boost_program_options-vc141-mt-x64;boost_program_options-vc141-mt;boost_program_options-vc140-mt-x64-1_74;boost_program_options-vc140-mt-x64;boost_program_options-vc140-mt;boost_program_options-mt-x64-1_74;boost_program_options-mt-x64;boost_program_options-mt;boost_program_options-mt;boost_program_options
[ Z:/BASE_ENV/CMake/share/cmake-3.18/Modules/FindBoost.cmake:2111 ] Searching for PROGRAM_OPTIONS_LIBRARY_DEBUG: boost_program_options-vc141-mt-gd-x64-1_74;boost_program_options-vc141-mt-gd-x64;boost_program_options-vc141-mt-gd;boost_program_options-vc140-mt-gd-x64-1_74;boost_program_options-vc140-mt-gd-x64;boost_program_options-vc140-mt-gd;boost_program_options-mt-gd-x64-1_74;boost_program_options-mt-gd-x64;boost_program_options-mt-gd;boost_program_options-mt;boost_program_options
[ Z:/BASE_ENV/CMake/share/cmake-3.18/Modules/FindBoost.cmake:2056 ] Searching for SYSTEM_LIBRARY_RELEASE: boost_system-vc141-mt-x64-1_74;boost_system-vc141-mt-x64;boost_system-vc141-mt;boost_system-vc140-mt-x64-1_74;boost_system-vc140-mt-x64;boost_system-vc140-mt;boost_system-mt-x64-1_74;boost_system-mt-x64;boost_system-mt;boost_system-mt;boost_system
[ Z:/BASE_ENV/CMake/share/cmake-3.18/Modules/FindBoost.cmake:2111 ] Searching for SYSTEM_LIBRARY_DEBUG: boost_system-vc141-mt-gd-x64-1_74;boost_system-vc141-mt-gd-x64;boost_system-vc141-mt-gd;boost_system-vc140-mt-gd-x64-1_74;boost_system-vc140-mt-gd-x64;boost_system-vc140-mt-gd;boost_system-mt-gd-x64-1_74;boost_system-mt-gd-x64;boost_system-mt-gd;boost_system-mt;boost_system
[ Z:/BASE_ENV/CMake/share/cmake-3.18/Modules/FindBoost.cmake:2056 ] Searching for SERIALIZATION_LIBRARY_RELEASE: boost_serialization-vc141-mt-x64-1_74;boost_serialization-vc141-mt-x64;boost_serialization-vc141-mt;boost_serialization-vc140-mt-x64-1_74;boost_serialization-vc140-mt-x64;boost_serialization-vc140-mt;boost_serialization-mt-x64-1_74;boost_serialization-mt-x64;boost_serialization-mt;boost_serialization-mt;boost_serialization
[ Z:/BASE_ENV/CMake/share/cmake-3.18/Modules/FindBoost.cmake:2111 ] Searching for SERIALIZATION_LIBRARY_DEBUG: boost_serialization-vc141-mt-gd-x64-1_74;boost_serialization-vc141-mt-gd-x64;boost_serialization-vc141-mt-gd;boost_serialization-vc140-mt-gd-x64-1_74;boost_serialization-vc140-mt-gd-x64;boost_serialization-vc140-mt-gd;boost_serialization-mt-gd-x64-1_74;boost_serialization-mt-gd-x64;boost_serialization-mt-gd;boost_serialization-mt;boost_serialization
[ Z:/BASE_ENV/CMake/share/cmake-3.18/Modules/FindBoost.cmake:2056 ] Searching for REGEX_LIBRARY_RELEASE: boost_regex-vc141-mt-x64-1_74;boost_regex-vc141-mt-x64;boost_regex-vc141-mt;boost_regex-vc140-mt-x64-1_74;boost_regex-vc140-mt-x64;boost_regex-vc140-mt;boost_regex-mt-x64-1_74;boost_regex-mt-x64;boost_regex-mt;boost_regex-mt;boost_regex
[ Z:/BASE_ENV/CMake/share/cmake-3.18/Modules/FindBoost.cmake:2111 ] Searching for REGEX_LIBRARY_DEBUG: boost_regex-vc141-mt-gd-x64-1_74;boost_regex-vc141-mt-gd-x64;boost_regex-vc141-mt-gd;boost_regex-vc140-mt-gd-x64-1_74;boost_regex-vc140-mt-gd-x64;boost_regex-vc140-mt-gd;boost_regex-mt-gd-x64-1_74;boost_regex-mt-gd-x64;boost_regex-mt-gd;boost_regex-mt;boost_regex
CMake Error at Z:/BASE_ENV/CMake/share/cmake-3.18/Modules/FindPackageHandleStandardArgs.cmake:165 (message):
  Could NOT find Boost (missing: iostreams program_options system
  serialization) (found version "1.74.0")
Call Stack (most recent call first):
  Z:/BASE_ENV/CMake/share/cmake-3.18/Modules/FindPackageHandleStandardArgs.cmake:458 (_FPHSA_FAILURE_MESSAGE)
  Z:/BASE_ENV/CMake/share/cmake-3.18/Modules/FindBoost.cmake:2177 (find_package_handle_standard_args)
  CMakeLists.txt:122 (FIND_PACKAGE)
```



## 2020/10/26 - 2020/10/28
### vs2019编译boost
进入boost解压的根目录，执行：
```sh
# 生成b2.exe
./bootstrap.bat
# 编译指定的工具集的库的版本(可能出现没有cl和cstddef的问题，见后面的注意)
.\b2.exe  --toolset=msvc-14.2  `
--address-model=64 `
--architecture=x86 `
--threading=multi `
--with-iostreams --with-program_options --with-system --with-serialization `
stage --stagedir="F:\BASE_ENV\forOpenMVS\boost_1_74_0\forOpenMVS"
# 可能需要使用boost追加编译zlib的库(github下源码)，如下：
.\b2.exe  --toolset=msvc-14.2  `
--address-model=64 `
--architecture=x86 `
--threading=multi `
--with-iostreams -sZLIB_SOURCE="F:\BASE_ENV\forOpenMVS\zlib-1.2.11" -sZLIB_INCLUDE="F:\BASE_ENV\forOpenMVS\zlib-1.2.11" `
--link=static --runtime-link=static `
stage --stagedir="F:\BASE_ENV\forOpenMVS\boost_1_74_0\forOpenMVS"
```
__注意： 出现找不到cl和cstddef的问题多半是环境变量的问题，编辑如下环境变量：__
- 1 path中添加(运行cl.exe): C:\Program Files (x86)\Microsoft Visual Studio\2019\Community\VC\Tools\MSVC\14.27.29110\bin\Hostx64\x64
- 2 添加变量: INCLUDE, 值: C:\Program Files (x86)\Microsoft Visual Studio\2019\Community\VC\Tools\MSVC\14.27.29110\include;C:\Program Files (x86)\Windows Kits\10\Include\10.0.18362.0\shared;C:\Program Files (x86)\Windows Kits\10\Include\10.0.18362.0\winrt;C:\Program Files (x86)\Windows Kits\10\Include\10.0.18362.0\um;C:\Program Files (x86)\Windows Kits\10\Include\10.0.18362.0\ucrt;
- 3 添加变量: LIB, 值: C:\Program Files (x86)\Microsoft Visual Studio\2019\Community\VC\Tools\MSVC\14.27.29110\lib\x64;C:\Program Files (x86)\Windows Kits\10\Lib\10.0.18362.0\um\x64;C:\Program Files (x86)\Windows Kits\10\Lib\10.0.18362.0\ucrt\x64;
### 编译OpenMVS
按照其官方的buildingWilki[https://github.com/cdcseacave/openMVS/wiki/Building](https://github.com/cdcseacave/openMVS/wiki/Building)将相关的依赖库放到其同级目录，新建build然后进入，执行的cmake指令如下：
```sh
# 在 windows terminal中执行(cmake -G "Visual Studio 14 Win64" path\to\source\dir)
cmake . ..\openMVS\ `
-G "Visual Studio 16 2019" `
-DVCG_ROOT="..\VCG" `
-DBOOST_INCLUDEDIR="F:/BASE_ENV/forOpenMVS/boost_1_74_0" `
-DBOOST_LIBRARYDIR="F:/BASE_ENV/forOpenMVS/boost_1_74_0/forOpenMVS" `
-DOpenCV_DIR="F:/BASE_ENV/forOpenMVS/opencv/build" `
-DGMP_INCLUDE_DIR="F:\BASE_ENV\forOpenMVS\gmp_mpfr\include" `
-DGMP_LIBRARIES="F:\BASE_ENV\forOpenMVS\gmp_mpfr\lib\libgmp-10.lib" `
-DMPFR_INCLUDE_DIR="F:\BASE_ENV\forOpenMVS\gmp_mpfr\include" `
-DMPFR_LIBRARIES="F:\BASE_ENV\forOpenMVS\gmp_mpfr\lib\libmpfr-4.lib" `
-DEIGEN_ROOT="F:\BASE_ENV\forOpenMVS\eigen" `
-DCERES_ROOT="F:\BASE_ENV\forOpenMVS\ceres-solver\build" `
-DJPEG_INCLUDE_DIRS="F:\BASE_ENV\forOpenMVS\jpegsr9" `
-DJPEG_LIBRARIES="F:\BASE_ENV\forOpenMVS\jpegsr9\libjpeg.lib"
```

生成sln文件后，报错日志如下：
```log
...<作者省略>
boost::iostreams::detail::zlib_base::zlib_base(void)" (??0zlib_base@detail@iostreams@boost@@IEAA@XZ)
5>MVS.lib(Scene.obj) : error LNK2001: unresolved external symbol "protected: __cdecl boost::iostreams::detail::zlib_base::~zlib_base(void)" (??1zlib_base@detail@iostreams@boost@@IEAA@XZ)
...<作者省略>
5>MVS.lib(Scene.obj) : error LNK2001: unresolved external symbol "int const 
6>libgmp.a(dcpi1_bdiv_qr.o) : error LNK2001: unresolved external symbol ___chkstk_ms
...<作者省略>
6>Done building project "ReconstructMesh.vcxproj" -- FAILED.
8>Done building project "TextureMesh.vcxproj" -- FAILED.
4>Finished generating code
4>InterfaceCOLMAP.vcxproj -> F:\BASE_ENV\forOpenMVS\build\bin\x64\Release\InterfaceCOLMAP.exe
9>------ Skipped Build: Project: INSTALL, Configuration: Release x64 ------
9>Project not selected to build for this solution configuration 
========== Build: 1 succeeded, 5 failed, 6 up-to-date, 3 skipped ==========
```

以上日志说明两个问题：
- 1: gmp和mpfr库有问题 -> 使用cgal的setup安装，然后进入auxiliary/gmp中有gmp和mpfr的库。
- 2: 编译的boost的iostream库with zlib有问题，zlib说有些符号无法解析:
  - 注意： boost的编译，会将编译结果存在build_dir（bin.v2）中然后拷贝到指定的lib目录下，这就造成，如果需要新编库，必须手动删除build_dir中生成的库文件，否则新编译库是不会overwrite的，而是直接从build_dir中复制到指定的lib目录下，于是： 编译带有zlib的库的时候，需要先将iostream库删除（指定的lib目录和build_dir中的库），然后重新编译。
- 3 .\b2.exe `
    --stage-dir="Z:\BASE_ENV\forOpenMVS\boost_1_62_0\vc14" `
    --adress-model=64 --build-type=complete
    低版本的默认使用gcc编译。


## 2020/10/29
### 0 OpenMVS读取图像依赖于jpeg, png等lib, 需要手动编好然后修改一下CMakeList.txt
```sh
# libjepg:文件下载： http://www.ijg.org/files/ (下载其中的jpeg9.zip或者jpeg9a.zip，具体看里面的readme)
解压进入根目录：
cp C:\Program Files (x86)\Microsoft SDKs\Windows\v7.1A\Include ./
cp jconfig.vc jconfig.h
nmake -f makefile.vc
```

### 1 使用OpenMVS:
### 1.0 修改OpenMVS以使其支持jpeg
修改：OpenMVS/libs/IO/CMakeLists.txt
SET (JPEG_INCLUDE_DIR "F:/BASE_ENV/forOpenMVS/jpegsr9")
SET (JPEG_LIBRARY "F:/BASE_ENV/forOpenMVS/jpegsr9/libjpeg.lib")

### 1.1 命令行调用OpenMVS
```sh
# 依赖于opencv的几个dll库
-a----       2020/10/24     20:22        3063296 opencv_calib3d450.dll
-a----       2020/10/29      9:50       17019904 opencv_core450.dll
-a----       2020/10/24     20:22         952320 opencv_features2d450.dll
-a----       2020/10/24     20:20         528896 opencv_flann450.dll
-a----       2020/10/24     20:21        3386880 opencv_imgcodecs450.dll
-a----       2020/10/24     20:21       29256192 opencv_imgproc450.dll
# 将文件名转小写
for i in $(ls); do cp ${i} ../lowerCaseImages/${i,,}; done
# openMVS贴图使用方式:
F:\BASE_ENV\forOpenMVS\build\bin\x64\Release\InterfaceVisualSFM.exe -i result.out -o result.mvs
F:\BASE_ENV\forOpenMVS\build\bin\x64\Release\TextureMesh.exe --mesh-file result_dense_mesh_simple.ply -i result.mvs -o result.ply
```

## 2020/10/30
### 1 LRU实现：(参考colmap中的utils/cache.h)
least recently used(will be discard)
```log
务必将模板类的声明和实现放在一起！
```

## 2020/11/02 - 11/03

### 1 编译MVE
参考：[https://github.com/simonfuhrmann/mve/wiki/Build-Instructions-for-Windows](https://github.com/simonfuhrmann/mve/wiki/Build-Instructions-for-Windows)
参考该链接完成编译即可，主要问题在于若下载很慢，可能需要你手动将文件下载到对应目录，其次：
__F:\BASE_ENV\forMVE_TEXRecon\mve\3rdparty\qt5\src\qt5\qtbase\qmake\generators\win32\msvc_vcproj.cpp__ 里说明，19版本不支持，使用15以及以上工具编译：
```cpp
QT_BEGIN_NAMESPACE
// Filter GUIDs (Do NOT change these!) ------------------------------
const char _GUIDSourceFiles[]          = "{4FC737F1-C7A5-4376-A066-2A32D752A2FF}";
const char _GUIDHeaderFiles[]          = "{93995380-89BD-4b04-88EB-625FBE52EBFB}";
const char _GUIDGeneratedFiles[]       = "{71ED8ED8-ACB9-4CE9-BBE1-E00B30144E11}";
const char _GUIDResourceFiles[]        = "{D9D6E242-F8AF-46E4-B9FD-80ECBC20BA3E}";
const char _GUIDLexYaccFiles[]         = "{E12AE0D2-192F-4d59-BD23-7D3FA58D3183}";
const char _GUIDTranslationFiles[]     = "{639EADAA-A684-42e4-A9AD-28FC9BCB8F7C}";
const char _GUIDFormFiles[]            = "{99349809-55BA-4b9d-BF79-8FDBB0286EB3}";
const char _GUIDExtraCompilerFiles[]   = "{E0D8C965-CC5F-43d7-AD63-FAEF0BBC0F85}";
const char _GUIDDeploymentFiles[]      = "{D9D6E243-F8AF-46E4-B9FD-80ECBC20BA3E}";
const char _GUIDDistributionFiles[]    = "{B83CAF91-C7BF-462F-B76C-EA11631F866C}";
QT_END_NAMESPACE
```
两次使用的编译命令：
```sh
cmake -G "Visual Studio 14 Win64" .
```
### 2 编译MVS-Texturing (texrecon)
- 2.1 下载tbb库：[https://github.com/oneapi-src/oneTBB/releases/tag/v2020.3](https://github.com/oneapi-src/oneTBB/releases/tag/v2020.3)
将之前编译的mve中的库和tbb都放到texrecon/3rdparty下面：

- 2.2 下载MVS-Texturing(和mve同级目录)使用分支：*__cmake__* -> [https://github.com/andre-schulz/mvs-texturing/tree/cmake](https://github.com/andre-schulz/mvs-texturing/tree/cmake)
配置完成以后，jpeg，tiff，png，zlib，mve_util的库需要在生成texrecon项目的时候在其属性中配置连接器对于这些库输入(会出现link err2019)：
```sh
cmake . ..\ `
-G "Visual Studio 14 Win64" `
-DMVE_INCLUDE_DIRS="F:\BASE_ENV\forMVE_TEXRecon\mve\libs" `
-DTBB_ROOT_DIR="F:\BASE_ENV\forMVE_TEXRecon\mvs-texturing\3rdparty\tbb" `
-DTBB_INCLUDE_DIRS="F:\BASE_ENV\forMVE_TEXRecon\mvs-texturing\3rdparty\tbb\include" `
-DTBB_LIBRARIES="F:\BASE_ENV\forMVE_TEXRecon\mvs-texturing\3rdparty\tbb\lib" `
-DPNG_PNG_INCLUDE_DIR="F:\BASE_ENV\forMVE_TEXRecon\mvs-texturing\3rdparty\png_tiff_zip_qt5\include" `
-DPNG_LIBRARY="F:\BASE_ENV\forMVE_TEXRecon\mvs-texturing\3rdparty\png_tiff_zip_qt5\lib" `
-DZLIB_INCLUDE_DIR="F:\BASE_ENV\forMVE_TEXRecon\mvs-texturing\3rdparty\png_tiff_zip_qt5\include" `
-DZLIB_LIBRARY="F:\BASE_ENV\forMVE_TEXRecon\mvs-texturing\3rdparty\png_tiff_zip_qt5\lib" `
-DJPEG_INCLUDE_DIR="F:\BASE_ENV\forMVE_TEXRecon\mvs-texturing\3rdparty\png_tiff_zip_qt5\include" `
-DJPEG_LIBRARY="F:\BASE_ENV\forMVE_TEXRecon\mvs-texturing\3rdparty\png_tiff_zip_qt5\lib" `
-DTIFF_INCLUDE_DIR="F:\BASE_ENV\forMVE_TEXRecon\mvs-texturing\3rdparty\png_tiff_zip_qt5\include" `
-DTIFF_LIBRARY="F:\BASE_ENV\forMVE_TEXRecon\mvs-texturing\3rdparty\png_tiff_zip_qt5\lib"
```
- 2.3 编译完成后，需要在texrecon.exe同级目录加入：
```log
jpeg62.dll*
libpng16.dll*
tiff.dll*
zlib.dll*
```
__注意： -1，为了适应我们的数据，需要对代码做一定的更改，给入的数据的flen必须是单位话以后的焦长。__
__注意： -2，输入数据的yz需要反转。__
__注意： -3，需要更改mve中的camera代码，在更改以后注意将对应的库替换掉，然后重新编译。或者修改输入的每张图片的相机参数，将其flen除以max(wight, height)__
- 2.4 texrecon使用方式：
```sh
# 使用如下脚本获得mvs-texture(texrecon)规定的数据格式。
sh turnYZ_in_camera_rot_and_translation.sh result.out camArgs 5433
# 运行该程序，注意：在windows下使用scene_dir，不要使用相对路径，使用绝对路径
F:/BASE_ENV/forMVE_TEXRecon/mvs-texturing/build/apps/texrecon/Release/texrecon.exe  --skip_geometric_visibility_test  F:/dataSets/1011OpenMVS/texrecon/scene201103/ result_dense_mesh_refined.ply textured
```
## 2020/11/10
### 1 MRF-based mosaicing(贴图)
主要参考:
[http://www.robots.ox.ac.uk/~vilem/SeamlessMosaicing.pdf](http://www.robots.ox.ac.uk/~vilem/SeamlessMosaicing.pdf)
主要思想：
mrf的每一个节点不是图片的像素，而是mesh中的三角片，然后定义好能量方程，LBP就是使这些能量方程迅速收敛的优化算法。
所谓的能量方程：
- 1 这个view对于这个face看的有多准，多清楚
- 2 face和它周围的faces（周围的faces可能来自于不同的views）之间，会有色差，这也是一方面的能量
## 2020/11/13 - 11/17
> ps: osg的PagedLod依赖于databasePager这个类(proxyNode也是依赖于该类)来实现动态调度，详情见：osg3 cookbook的321面。
> ps: osg中使用行主序矩阵实现矩阵变换，所以对于点的变换，按照前乘实现。
### 1 关于读取osgb文件的方法：
主要修改PrimitiveFunctor，然后更改nodevisitor即可。
A PrimitiveFunctor is used (in conjunction with osg::Drawable::accept (PrimitiveFunctor&)) to get access to the primitives that compose the things drawn by OSG.
标注工具使用labelimage
为什么运行cesium的官方的实例时，需要将使用到的属性和部件放到import中
## 2020/11/21
### 1 使用cesium加载gltf的模型报错：
问题描述：
在fregata项目中尝试添加贴地运动小车
参考实现代码：
https://sandcastle.cesium.com/?src=Clamp%20to%203D%20Tiles.html&label=3D%20Tiles
错误日志： //实际上就是没有按照webpack的配置来配路径而已
```log
RuntimeError {name: "RuntimeError", message: "Failed to load model: Cesium_Air.glb↵Unexpected token < in JSON at position 0", stack: "Error↵    at new RuntimeError (webpack-internal://…e_modules/cesium/Source/ThirdParty/when.js:646:4)"}message: "Failed to load model: Cesium_Air.glb↵Unexpected token < in JSON at position 0"name: "RuntimeError"stack: "Error↵    at new RuntimeError (webpack-internal:///./node_modules/cesium/Source/Core/RuntimeError.js:40:11)↵    at eval (webpack-internal:///./node_modules/cesium/Source/Scene/ModelUtility.js:185:32)↵    at Promise.eval [as then] (webpack-internal:///./node_modules/cesium/Source/ThirdParty/when.js:216:33)↵    at eval (webpack-internal:///./node_modules/cesium/Source/ThirdParty/when.js:296:13)↵    at processQueue (webpack-internal:///./node_modules/cesium/Source/ThirdParty/when.js:646:4)↵    at _resolve (webpack-internal:///./node_modules/cesium/Source/ThirdParty/when.js:332:4)↵    at promiseReject (webpack-internal:///./node_modules/cesium/Source/ThirdParty/when.js:365:11)↵    at Promise.eval [as then] (webpack-internal:///./node_modules/cesium/Source/ThirdParty/when.js:216:33)↵    at eval (webpack-internal:///./node_modules/cesium/Source/ThirdParty/when.js:297:7)↵    at processQueue (webpack-internal:///./node_modules/cesium/Source/ThirdParty/when.js:646:4)"__proto__: 
```
### 1 osg实现物体拖拽
调用osg::Dragger即可；
官方例子： [https://github.com/openscenegraph/OpenSceneGraph/blob/master/examples/osgmanipulator/osgmanipulator.cpp](https://github.com/openscenegraph/OpenSceneGraph/blob/master/examples/osgmanipulator/osgmanipulator.cpp)
osg实现相交代码：
```cpp
bool View::computeIntersections(float x,float y, osgUtil::LineSegmentIntersector::Intersections& intersections, osg::Node::NodeMask traversalMask)
{
    float local_x, local_y;
    const osg::Camera* camera = getCameraContainingPosition(x, y, local_x, local_y);
    OSG_INFO<<"computeIntersections("<<x<<", "<<y<<") local_x="<<local_x<<", local_y="<<local_y<<std::endl;
    if (camera) return computeIntersections(camera, (camera->getViewport()==0)?osgUtil::Intersector::PROJECTION : osgUtil::Intersector::WINDOW, local_x, local_y, intersections, traversalMask);
    else return false;
}
bool View::computeIntersections(const osg::Camera* camera, osgUtil::Intersector::CoordinateFrame cf, float x,float y, const osg::NodePath& nodePath, osgUtil::LineSegmentIntersector::Intersections& intersections,osg::Node::NodeMask traversalMask)
{
    if (!camera || nodePath.empty()) return false;
    osg::Matrixd matrix;
    if (nodePath.size()>1)
    {
        osg::NodePath prunedNodePath(nodePath.begin(),nodePath.end()-1);
        matrix = osg::computeLocalToWorld(prunedNodePath);
    }
    matrix.postMult(camera->getViewMatrix());
    matrix.postMult(camera->getProjectionMatrix());
    double zNear = -1.0;
    double zFar = 1.0;
    if (cf==osgUtil::Intersector::WINDOW && camera->getViewport())
    {
        matrix.postMult(camera->getViewport()->computeWindowMatrix());
        zNear = 0.0;
        zFar = 1.0;
    }
    osg::Matrixd inverse;
    inverse.invert(matrix);
    osg::Vec3d startVertex = osg::Vec3d(x,y,zNear) * inverse;
    osg::Vec3d endVertex = osg::Vec3d(x,y,zFar) * inverse;
    osg::ref_ptr< osgUtil::LineSegmentIntersector > picker = new osgUtil::LineSegmentIntersector(osgUtil::Intersector::MODEL, startVertex, endVertex);
    osgUtil::IntersectionVisitor iv(picker.get());
    iv.setTraversalMask(traversalMask);
    nodePath.back()->accept(iv);
    if (picker->containsIntersections())
    {
        intersections = picker->getIntersections();
        return true;
    }
    else
    {
        intersections.clear();
        return false;
    }
}
```
### 2 自己实现拖拽效果
```cpp
	//used for drag the bounding box
	//osg::ref_ptr<osgViewer::View> pViewer = NULL;
	//Scene *                       pScene = NULL;
	bool                          ifPicked = false;       // if a object is picked
	osg::MatrixTransform *        pPickedObject = NULL;   // the picked object 
	bool                          lButtonDown = false;
	bool                          rButtonDown = false;
	osg::Vec3                     firstIntersectionPoint; // when picking obj, the first intersect point
	float                         z;                      // firstIntersectionPoint's z value in frustrum space
	osg::Vec3                     stPoint;                // drag start point
	osg::Vec3                     endPoint;               // drag end point
	osg::Matrix                   stPos;                  // starting pos
	
	void pickByRay(float x, float y);
	osg::Vec3 screen2World(float x, float y);
	osg::Vec3 world2Screen(osg::Vec3& wV);
//事件处理函数
bool CPickHandler::handle(const osgGA::GUIEventAdapter& ea, osgGA::GUIActionAdapter& us)
{
	osgViewer::Viewer *viewer = dynamic_cast<osgViewer::Viewer*>(&us);
	if (!viewer)//如果转换失败则直接退出
	{
		return false;
	}
	CString s;
	switch (ea.getEventType())
	{
		case osgGA::GUIEventAdapter::PUSH: {
			if (viewer) {
				int button = ea.getButton();
				if (button == osgGA::GUIEventAdapter::LEFT_MOUSE_BUTTON) {
					lButtonDown = true;
					//MessageBox(NULL, "push doing!1", "hint", MB_OK);
					pickByRay(ea.getX(), ea.getY());
					//MessageBox(NULL, "push doing!2", "hint", MB_OK);
					if (pPickedObject) {
						stPoint = screen2World(ea.getX(), ea.getY());
						stPos = pPickedObject->getMatrix();
						//MessageBox(NULL, "push doing!2.1", "hint", MB_OK);
						// when push and drag, we want to shut down the camera manipulator
						// till the drag motion is done
						mViewer->setCameraManipulator(NULL);
						//mViewer->getCameraManipulator()-
						//mViewer->setUpdateOperations
					}
				}
				else {
					lButtonDown = false;
				}
			}
		return false;
	    }
	    case  osgGA::GUIEventAdapter::DRAG: {
	    	if (pPickedObject&&lButtonDown)	{
	    		endPoint = screen2World(ea.getX(), ea.getY());
				stPoint.z() = endPoint.z() = z;
	    		float dx = endPoint.x() - stPoint.x();
	    		float dy = endPoint.y() - stPoint.y();
	    		//float dz = endPoint.z() - stPoint.z() = 0;
	    		std::cout << dx << "  " << dy << std::endl;
	    		if (fabs(dx) + fabs(dy) < 0.06) {
	    		    std::cout << "small movement" << dx << "  " << dy << std::endl;
	    		}
	    		pPickedObject->setMatrix(stPos * osg::Matrix::translate(dx, 0, dy));
				//cosg->mViewer->setCameraManipulator(cosg->trackball, false);
				//MessageBox(NULL, "drag doing!", "hint", MB_OK);
	    	}
	    	return false;
	    }
	    case osgGA::GUIEventAdapter::RELEASE: {
			cosg->mViewer->setCameraManipulator(cosg->trackball, false);
	    	pPickedObject = false;
	    	return false;
	    }
	    case (osgGA::GUIEventAdapter::DOUBLECLICK): {
	    	MessageBox(NULL, "double click doing!", 0, MB_OK);
	    }
	default:
		return false;
	}
}
void CPickHandler::pickByRay(float x, float y) {
	osgUtil::LineSegmentIntersector::Intersections intersections;
	if (mViewer->computeIntersections(x, y, intersections)) {
		// get the first intersected object
		osgUtil::LineSegmentIntersector::Intersections::iterator hitr = intersections.begin();
		osg::NodePath getNodePath = hitr->nodePath;
		
		// find the object's matrix transform
		for (int i = getNodePath.size() - 1; i >= 0; --i) {
			osg::MatrixTransform* mt = dynamic_cast<osg::MatrixTransform*>(getNodePath[i]);
			if (mt == NULL) {
				continue;
			}
			else {
				pPickedObject = mt;
				ifPicked = true;
			    firstIntersectionPoint = hitr->getLocalIntersectPoint(); //in world 
				z = world2Screen(firstIntersectionPoint).z(); // in screen
				//MessageBox(NULL, tmp, "hint", MB_OK);
			}
		}
	}
	else {
		ifPicked = false;
	}
}
osg::Vec3 CPickHandler::screen2World(float x, float y)
{
	osg::Vec3 vec3;
	osg::ref_ptr<osg::Camera> camera = mViewer->getCamera();
	osg::Vec3 vScreen(x, y, 0);
	osg::Matrix mVPW = camera->getViewMatrix() * camera->getProjectionMatrix() * camera->getViewport()->computeWindowMatrix();
	osg::Matrix invertVPW;
	invertVPW.invert(mVPW);
	vec3 = vScreen * invertVPW;
	return vec3;
}
osg::Vec3 CPickHandler::world2Screen(osg::Vec3& wV) {
	osg::ref_ptr<osg::Camera> camera = mViewer->getCamera();
	osg::Matrix mVPW = camera->getViewMatrix() * camera->getProjectionMatrix() * camera->getViewport()->computeWindowMatrix();
	return wV * mVPW;
}
//osg::Vec3 CPickHandler::screen2World(float x, float y) {
//	osg::Vec3 point(0, 0, 0);
//	osgUtil::LineSegmentIntersector::Intersections intersections;
//	if (mViewer->computeIntersections(x, y, intersections)) {
//		osgUtil::LineSegmentIntersector::Intersections::iterator itr = intersections.begin();
//		point[0] = itr->getWorldIntersectPoint().x();
//		point[1] = itr->getWorldIntersectPoint().y();
//		point[2] = itr->getWorldIntersectPoint().z();
//	}
//	return point;
//}
```
```cpp
/*绘制并渲染几何体的主要步骤：
1.创建各种向量数据，如顶点、纹理坐标、颜色、法线。顶点数据按照逆时针顺序添加，以确保背面剔除的正确
2.实例化几何对象osg::Geometry，设置顶点坐标数组、纹理坐标数组、颜色数组、法线数组、绑定方式和数据解析
3.加入叶节点绘制并渲染
*/
osg::ref_ptr<osg::Node> createQuad(osg::ref_ptr<osg::Vec3Array>& v)
{
	//创建一个叶节点对象
	osg::ref_ptr<osg::Geode> geode = new osg::Geode();
	//创建一个几何体对象
	osg::ref_ptr<osg::Geometry> geom = new osg::Geometry();
	////创建顶点数组，注意顶点的添加顺序是逆时针的
	//osg::ref_ptr<osg::Vec3Array> v = new osg::Vec3Array();
	////添加数据
	//v->push_back(osg::Vec3(0.0f, 0.0f, 0.0f));
	//v->push_back(osg::Vec3(1.0f, 0.0f, 0.0f));
	//v->push_back(osg::Vec3(1.0f, 0.0f, 1.0f));
	//v->push_back(osg::Vec3(0.0f, 0.0f, 1.0f));
	//设置顶点数据setVertexArray(Array *array)
	geom->setVertexArray(v.get());
	//创建纹理数组
	osg::ref_ptr<osg::Vec2Array> vt = new osg::Vec2Array();
	//添加数据
	vt->push_back(osg::Vec2(0.0f, 0.0f));
	vt->push_back(osg::Vec2(1.0f, 0.0f));
	vt->push_back(osg::Vec2(1.0f, 1.0f));
	vt->push_back(osg::Vec2(0.0f, 1.0f));
	//设置纹理坐标数组setTexCoordArray(unsigned int unit, Array *)参数纹理单元/纹理坐标数组
	geom->setTexCoordArray(0, vt.get());
	//数据绑定：法线、颜色，绑定方式为：
	//BIND_OFF不启动用绑定/BIND_OVERALL绑定全部顶点/BIND_PER_PRIMITIVE_SET单个绘图基元绑定/BIND_PER_PRIMITIVE单个独立的绘图基元绑定/BIND_PER_VERTIE单个顶点绑定
	//采用BIND_PER_PRIMITIVE绑定方式，则OSG采用glBegin()/glEnd()函数进行渲染，因为该绑定方式为每个独立的几何图元设置一种绑定方式
	//创建颜色数组
	osg::ref_ptr<osg::Vec4Array> vc = new osg::Vec4Array();
	//添加数据
	vc->push_back(osg::Vec4(1.0f, 0.0f, 0.0f, 1.0f));
	vc->push_back(osg::Vec4(0.0f, 1.0f, 0.0f, 1.0f));
	vc->push_back(osg::Vec4(0.0f, 0.0f, 1.0f, 1.0f));
	vc->push_back(osg::Vec4(1.0f, 1.0f, 0.0f, 1.0f));
	//设置颜色数组setColorArray(Array *array)
	geom->setColorArray(vc.get());
	//设置颜色的绑定方式setColorBinding(AttributeBinding ab)为单个顶点
	geom->setColorBinding(osg::Geometry::BIND_PER_VERTEX);
	//创建法线数组
	osg::ref_ptr<osg::Vec3Array> nc = new osg::Vec3Array();
	//添加法线
	nc->push_back(osg::Vec3(0.0f, -1.0f, 0.0f));
	//设置法线数组setNormalArray(Array *array)
	geom->setNormalArray(nc.get());
	//设置法线的绑定方式setNormalBinding(AttributeBinding ab)为全部顶点
	geom->setNormalBinding(osg::Geometry::BIND_OVERALL);
	//添加图元，绘制基元为四边形
	//数据解析，即指定向量数据和绑定方式后，指定渲染几何体的方式，不同方式渲染出的图形不同，即时效果相同，可能面数或内部机制等也有区别，函数为：
	//bool addPrimitiveSet(PrimitiveSet *primitiveset)参数说明：osg::PrimitiveSet是无法初始化的虚基类，因此主要调用它的子类指定数据渲染，最常用为osg::DrawArrays
	//osg::DrawArrays(GLenum mode, GLint first, GLsizei count)参数为指定的绘图基元、绘制几何体的第一个顶点数在指定顶点的位置数、使用的顶点的总数
	//PrimitiveSet类继承自osg::Object虚基类，但不具备一般一般场景中的特性，PrimitiveSet类主要封装了OpenGL的绘图基元，常见绘图基元如下
	//POINTS点/LINES线/LINE_STRIP多线段/LINE_LOOP封闭线
	//TRIANGLES一系列三角形(不共顶点)/TRIANGLE_STRIP一系列三角形(共用后面两个顶点)/TRIANGLE_FAN一系列三角形，顶点顺序与上一条语句绘制的三角形不同
	//QUADS四边形/QUAD_STRIP一系列四边形/POLYGON多边形
	geom->addPrimitiveSet(new osg::DrawArrays(osg::PrimitiveSet::QUADS, 0, 4));
	//添加到叶节点
	geode->addDrawable(geom.get());
	return geode.get();
}
```
## 2020/12/25 - 
### 0 模型精度渲染问题
meshlab读取模型时渲染的默认精度是float
osg渲染时也是float，这就导致了，转化成大地坐标系之后，比如3301412.7829会变成3301412.25之类的数据，
导致模型出现光栅效果。
如果需要读写自己的模型格式，考虑使用osg的注册器，注册自己模型读写方法。
### 1 从贴图中恢复出坐标
恢复坐标在重建软件中实现，然后转到体积测量的软件。
### 2 计算体积等(包括距离，面积，体积计算)功能
基于osgb的实现，然后解决0号问题
> fft2d: https://www.robots.ox.ac.uk/~az/lectures/ia/lect2.pd
>        https://www.zhihu.com/question/22611929/answer/341436331
### 3 实现步骤
- 1 东湖高新数据，哪些标记点，出现在哪些图片中，这些标记点的像素坐标:_config in yaml, transfer data in json_
```yaml
dataType: 文件表示的数据类型
metaData: 描述数据
imagesDir: 存储图片的目录
imageNameList: 图片名的列表
targetPointsAnnotation:
- point1:               # 第一个打标点的标注的像素坐标信息
    shownInImages:      # 第一个打标点出现在哪些图片中
    - 1.jpg
    - 2.jpg
    pixelPositions:     # 第一个打标点在出现的图片中对应的坐标
    - x: -2             # 对于该点对，则对应于point1在1.jpg中出现的坐标，图片的像素坐标以图像的中心点为原点
      y: -3
    - x: -2             # 对于该点对，则对应于point1在2.jpg中出现的坐标
      y: -3
- point2:               # 第二个打标点存储的像素坐标信息
    shownInImages:
    - 2.jpg
    - 3.jpg
    pixelPositions:
    - x: -2
      y: -3
    - x: -2
      y: -3
```
存储的信息格式如下列json所示，存储要求见上面的yaml注释
```json
{
  "dataType": "pixels annotations",
  "metaData": "this file try to store the information of the target points's pixel Positions on images where they may be on",
  "imagesDir": "D:\\images",
  "imagesNameList": [
    "1.jpg",
    "2.jpg",
    "3.jpg",
    "4.jpg"
  ],
  "targetPointsAnnotation": [
    {
      "point1": {
        "shownInImages": [
          "1.jpg",
          "2.jpg"
        ],
        "pixelPositions": [
          {"x": -2, "y": -3},
          {"x": -2, "y": -3}
        ]
      }
    },
    {
      "point2": {
        "shownInImages": [
          "2.jpg", 
          "3.jpg"
        ],
        "pixelPositions": [
          {"x": -2, "y": -3},
          {"x": -2, "y": -3}
        ]
      }
    }
  ]
```
## 2020/03/01 - 2020/03/26
### 1 osgb的内容组织以及读写
### 2 贴图的原理
### 2.0 使用phab比较两次提交的方法：
```
git log
git diff 808ed23da88251d7ff8df369c17441a574b00a98 1ebb2439e14bfe9f46e68c3b27c4807477a3db55 > a.txt
在phab中Diffrential中创建diff： 粘贴进入a.txt的代码即可
```
## 2020/04/13
### 1 修改模型：
```sh
# 本来apaqi.ive导弹模型头垂直屏幕向里面，之后头朝上，机身平行于屏幕
osgconv apaqi.ive apaqi.obj
# 绕着(0,1,1)旋转模型180度即可
osgconv -o 180-0,1,1 apaqi.ive apaqi_x-90_y180.obj
# 自动批量转换成gltf：
## step1: from ive to obj
for modelName in $(ls models | grep ive | sed s/.ive//g); do
    osgconv models/${modelName}.ive -o 180-0,1,1 models/${modelName}.obj
done;
## step2： from obj to gltf
for modelName in $(ls models | grep ive | sed s/.ive//g); do
    node bin/obj2gltf.js -i models/${modelName}.obj -o models/${modelName}.gltf
done;
```
## 2021/04/22 shit hexo
### 1 github初始化仓库 
初始化git repo: 地址如下
https://github.com/xychen5/xychen5.github.io.git
### 2 安装相关依赖
```sh
npm install -g hexo
hexo init blogs
cd blogs
npm install -s hexo-theme-next # 安装主题
npm install --save hexo-deployer-git # 安装专用git工具
hexo s # 本地测试一下是否能正常运行
```
### 3 部署 
编辑blogs/_config.yml的末尾如下：
```yml
# Extensions
## Plugins: https://hexo.io/plugins/
## Themes: https://hexo.io/themes/
theme: next
# Deployment
## Docs: https://hexo.io/docs/one-command-deployment
deploy:
  type: git
  repo: https://github.com/xychen5/xychen5.github.io.git
  branch: main
```
部署如下：
```sh
hexo clean && hexo g -d
cp .\node_modules\hexo-theme-next\_config.yml ./_config.next.yml # 将next的配置放到项目根目录，避免编辑第三方库里的yml
```
### 4 博客写作分类以及标签以及使用技巧
- 1 https://linlif.github.io/2017/05/27/Hexo%E4%BD%BF%E7%94%A8%E6%94%BB%E7%95%A5-%E6%B7%BB%E5%8A%A0%E5%88%86%E7%B1%BB%E5%8F%8A%E6%A0%87%E7%AD%BE/
- 2 官方guide: [https://hexo.io/docs/writing](https://hexo.io/docs/writing)
### 5 将hexo生成的网站(会推到xychen5.github.io库里)和自己写的markdown文件分开
- 1 初始化source库，然后将其推到某个远程仓库(github,gitlab,gitee...etc)
```sh
cd source
git init
git remote add origin <你的空repo地址>
git add .
git commit -m 'init'
git push -u origin master
```
- 2 向blogs/package.json中添加发布脚本：(添加了 npm run pub对应的pub)， 若整个博文没有任何改变，运行该命令会报错
- 2 然后在blogs/package.json加入：
```sh
  "scripts": {
    "build": "hexo generate",
    "clean": "hexo clean",
    "deploy": "hexo deploy",
    "server": "hexo server",
    "pub": "cd source && git add ./* && git commit -m 'upate' && git push && cd .. && hexo clean && hexo g -d"
  },
```
### 6 使用GitHub的图片床
主要参考：[https://github.com/XPoet/picx](https://github.com/XPoet/picx)
生成toke后记得复制: https://github.com/settings/tokens
## 2021/04/26
### 1 wsl迁移
```
首先查看所有分发版本
wsl -l --all  -v
  NAME STATE VERSION
 * Ubuntu-20.04 Running 2
导出分发版为tar文件到d盘
wsl --export Ubuntu-20.04 d:\ubuntu20.04.tar
注销当前分发版
wsl --unregister Ubuntu-20.04
重新导入并安装分发版在d:\ubuntu
wsl --import Ubuntu-20.04 d:\ubuntu d:\ubuntu20.04.tar --version 2
设置默认登陆用户为安装时用户名
ubuntu2004 config --default-user Username
删除tar文件(可选)
del d:\ubuntu20.04.tar
```
### 2 切换内核
```
下载安装: https://wslstorestorage.blob.core.windows.net/wslblob/wsl_update_x64.msi
wsl -l -v
wsl --set-version Ubuntu-20.04 2
wsl -l -v 
```
## 2021/04/28
### 1 hexo渲染latex
```
npm uninstall hexo-math --save
npm install hexo-renderer-mathjax --save
编辑hexo的_config.yml的配置:
# MathJax Support
mathjax:
  enable: true
  per_page: true
对需要渲染的博文加入matxjax支持：
---
title: Hexo渲染LaTeX公式关键
date: 2020-09-30 22:27:01
mathjax: true
--
```
## 2021/05/06 编译colmap
### 1 前期准备
#### 1 github上下载colmap稳定版源码: 
https://github.com/colmap/colmap/archive/refs/tags/3.6.zip
之后解压进入，执行： git init
#### 2 确保编译环境
- 1 确保你的vs不是vs2019 16.9.3以及以上，否则会有奇怪的cuda错误, 解决方案是：
  - 1.1 将vs2019卸载
  - 1.2 去[https://docs.microsoft.com/en-us/visualstudio/releases/2019/history#installing-an-earlier-release](https://docs.microsoft.com/en-us/visualstudio/releases/2019/history#installing-an-earlier-release)下载vs2019 16.8.5，然后安装v140，v141的生成工具
- 2 如果本篇博客所有内容都详细读完，任然无法成功编译colmap，那就装VS2015，然后用他的生成工具（cmake -G 参数指定编译器版本，命令行里输入cmake -G），项目打开还是可以用vs2019的。
然后将编译器加入环境变量：
C:\Program Files (x86)\Microsoft Visual Studio\2019\Community\VC\Tools\MSVC\14.16.27023\bin\HostX64\x64
输入cl能看到输出即可.
### 2 依赖安装
#### 2.1 boost 直接安装(推荐下载vs2015版本，我用的是v_1_73)
[https://boostorg.jfrog.io/artifactory/main/release/1.64.0/binaries/](https://boostorg.jfrog.io/artifactory/main/release/1.64.0/binaries)
```sh
boost使用源码编译的静态方式编译：
```sh
.\b2.exe  --toolset=msvc-14.2 `
--address-model=64 `
--architecture=x86 `
--threading=multi `
-sZLIB_SOURCE="F:\BASE_ENV\forOpenMVS\zlib-1.2.11" -sZLIB_INCLUDE="F:\BASE_ENV\forOpenMVS\zlib-1.2.11" `
--with-iostreams --with-iostreams --with-log --with-program_options --with-graph --with-test --with-regex --with-filesystem `
--link=static --runtime-link=shared --build-type=complete `
stage --stagedir="F:\BASE_ENV\forOpenMVS\boost_1_66_0\msvc142_linkStatic_runShared" `
```
#### 2.2 安装GMP和MFPR
- 0 不想要自己折腾： 参考： [https://github.com/emphasis87/libmpfr-msys2-mingw64](https://github.com/emphasis87/libmpfr-msys2-mingw64)，这里面应该有现成的库。
- 1 安装Cygwin
```sh
Setup Environment
Install Cygwin, add the following packages to the default installation: 
gcc-core
gcc-g++
libgcc
m4
make #不知为何安装后在Cygwin根目录下搜不到make程序，见下面步骤2安装make
cmake
bash
Add the following Environment Variable to the User PATH: C:\Program Files (x86)\Microsoft Visual Studio\2017\Enterprise\VC\Tools\MSVC\14.15.26726\bin\Hostx64\x64
This is so you can use the lib command. Your lib.exe may be located elsewhere.
```
安装好Cygwin以及一些依赖以后，在其根目录(方便说明记为： CygwinRoot="D:\CygwinRooto")下的bin/minnty.exe是其终端入口，然后每次打开该终端，进入的是：$CygwinRoot/home/$(userName)， 运行"cd /"后就可以理解了； 
- 2 下载并安装make
  - 2.1 从如下网址下载make的源码，https://ftp.gnu.org/gnu/make/，然后解压
  - 2.2 打开Cygwin64 Terminal命令行，进入源码根目录，然后运行：configure && ./build.sh
  - 2.3 编译得到了make.exe后将其移动到Cygwin的bin目录下
- 3 编译gmp
运行两个： ./configure 和 make install
```sh
./configure --prefix=/home/chenxy/mylibs/newTry/gmp-6.2.0/build/static --enable-static --disable-shared
configure: summary of build options:
  Version:           GNU MP 6.2.0
  Host type:         skylake-pc-cygwin
  ABI:               64
  Install prefix:    /home/chenxy/mylibs/newTry/gmp-6.2.0/build/static
  Compiler:          gcc
  Static libraries:  yes
  Shared libraries:  no
```
编译结果（默认生成的是static的数据）：
```log
@nash-5 ~/mylibs/gmp-6.2.0
$ ls /usr/local/include/
gmp.h
@nash-5 ~/mylibs/gmp-6.2.0
$ ls /usr/local/lib/
libgmp.a  libgmp.la  pkgconfig
```
生成动态连接库（注意： 动态连接库和静态连接库的.h文件不同，所以注意分成2个文件夹，至少对于gmp是如此）：
```sh
./configure --prefix=/home/chenxy/mylibs/gmp-6.2.0/build/shared --enable-shared --disable-static
```
- 4 编译mfpr（需要gmp的依赖，而且是动态连接库）
进入mfpr的根目录：
运行./configure：
```log
checking for gmp.h... no
configure: error: gmp.h can't be found, or is unusable.
```
运行./configure --help
```sh
···
  --with-gmp-include=DIR  GMP include directory
  --with-gmp-lib=DIR      GMP lib directory
···
```
所以：
```sh
./configure --prefix=/home/chenxy/mylibs/newTry/mpfr-4.1.0/build/static \
--enable-static --disable-shared \
--with-gmp-include=/home/chenxy/mylibs/newTry/gmp-6.2.0/build/static/include \
--with-gmp-lib=/home/chenxy/mylibs/newTry/gmp-6.2.0/build/staic/lib
make install
```
```sh
./configure --prefix=/home/chenxy/mylibs/mpfr-4.1.0/build/static \
--with-gmp-include=/home/chenxy/mylibs/gmp-6.2.0/build/static/include \
--with-gmp-lib=/home/chenxy/mylibs/gmp-6.2.0/build/static/lib \
--enable-static --disable-shared
```
#### 2.3 其他依赖build.py会帮你下载编译
确保你能够流畅访问github，否则需要你自己下载然后修改build.py。
### 3 编译colmap
#### 3.1 对编译文件和某些源文件的修改如下：
```diff
diff --git a/CMakeLists.txt b/CMakeLists.txt
index 7333a04..d73a6ad 100755
--- a/CMakeLists.txt
+++ b/CMakeLists.txt
@@ -72,8 +72,10 @@ endif()
 
 if(BOOST_STATIC)
     set(Boost_USE_STATIC_LIBS ON)
+    # message("@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@ using static boost", ${BOOST_STATIC})
 else()
     add_definitions("-DBOOST_TEST_DYN_LINK")
+    # message("@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@ using dll boost", ${BOOST_STATIC})
 endif()
 
 ################################################################################
@@ -86,6 +88,7 @@ endif()
 
 find_package(Ceres REQUIRED)
 
+set(Boost_DEBUG ON)
 find_package(Boost REQUIRED COMPONENTS
              program_options
              filesystem
diff --git a/scripts/python/build.py b/scripts/python/build.py
index 89dff59..fe1e4c4 100644
--- a/scripts/python/build.py
+++ b/scripts/python/build.py
@@ -75,10 +75,12 @@ def parse_args():
                         help="The path to the folder containing Boost, "
                              "e.g., under Windows: "
                              "C:/local/boost_1_64_0/lib64-msvc-12.0")
+    parser.add_argument("--boost_include_dir", default="F:/BASE_ENV/forOpenMVS/boost_1_73_0_v140")
+    parser.add_argument("--boost_lib_dir", default="F:/BASE_ENV/forOpenMVS/boost_1_73_0_v140/lib64-msvc-14.0")
     parser.add_argument("--cgal_path", default="",
                         help="The path to the folder containing CGAL, "
                              "e.g., under Windows: C:/dev/CGAL-4.11.2/build")
-    parser.add_argument("--cuda_path", default="",
+    parser.add_argument("--cuda_path", default="C:/Program Files/NVIDIA GPU Computing Toolkit/CUDA/v10.2",
                         help="The path to the folder containing CUDA, "
                              "e.g., under Windows: C:/Program Files/NVIDIA GPU "
                              "Computing Toolkit/CUDA/v8.0")
@@ -108,7 +110,7 @@ def parse_args():
                         help="Whether to build unit tests")
     parser.add_argument("--build_type", default="Release",
                         help="Build type, e.g., Debug, Release, RelWithDebInfo")
-    parser.add_argument("--cmake_generator", default="",
+    parser.add_argument("--cmake_generator", default="Visual Studio 14",
                         help="CMake generator, e.g., Visual Studio 14")
     parser.add_argument("--no_ssl_verification",
                         dest="ssl_verification", action="store_false",
@@ -429,8 +431,28 @@ def build_colmap(args):
         extra_config_args.append(
             "-DBOOST_ROOT={}".format(args.boost_path))
         extra_config_args.append(
-            "-DBOOST_LIBRARYDIR={}".format(args.boost_path))
-
+            "-DBOOST_INCLUDEDIR={}".format(args.boost_include_dir))
+        extra_config_args.append(
+            "-DBOOST_LIBRARYDIR={}".format(args.boost_lib_dir))
+        # print("BOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOST: ", extra_config_args)
+        # extra_config_args.append("-DBOOST_STATIC=ON")
+        # extra_config_args.append("-DBoost_USE_STATIC_LIBS=ON")
+        # extra_config_args.append("-DBoost_USE_MULTITHREADED=ON")
+        # extra_config_args.append("-DBoost_USE_STATIC_RUNTIME=ON")
+        # extra_config_args.append("-DBOOST_ALL_DYN_LINK=ON")
+    
+    # -DGMP_INCLUDE_DIR="F:\BASE_ENV\forOpenMVS\gmp_mpfr\include" `
+    # -DGMP_LIBRARIES="F:\BASE_ENV\forOpenMVS\gmp_mpfr\lib\libgmp-10.lib" `
+    # -DMPFR_INCLUDE_DIR="F:\BASE_ENV\forOpenMVS\gmp_mpfr\include" `
+    # -DMPFR_LIBRARIES="F:\BASE_ENV\forOpenMVS\gmp_mpfr\lib\libmpfr-4.lib" 
+    extra_config_args.append(
+        "-DGMP_INCLUDE_DIR={}".format("F:/BASE_ENV/forOpenMVS/gmp_mpfr/include"))
+    extra_config_args.append(
+        "-DGMP_LIBRARIES={}".format("F:/BASE_ENV/forOpenMVS/gmp_mpfr/lib/libgmp-10.lib"))
+    extra_config_args.append(
+        "-DMPFR_INCLUDE_DIR={}".format("F:/BASE_ENV/forOpenMVS/gmp_mpfr/include"))
+    extra_config_args.append(
+        "-DMPFR_LIBRARIES={}".format("F:/BASE_ENV/forOpenMVS/gmp_mpfr/lib/libmpfr-4.lib"))
     if args.cuda_path != "":
         extra_config_args.append(
             "-DCUDA_TOOLKIT_ROOT_DIR={}".format(args.cuda_path))
@@ -479,6 +501,8 @@ def build_post_process(args):
                         os.path.basename(lapack_path)))
 
         if args.qt_path:
+            print("copying !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!", os.path.join(args.qt_path, "bin/Qt5Core.dll"))
+            print("copying !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!", os.path.join(args.install_path, "lib/Qt5Core.dll"))
             copy_file_if_not_exists(
                 os.path.join(args.qt_path, "bin/Qt5Core.dll"),
                 os.path.join(args.install_path, "lib/Qt5Core.dll"))
diff --git a/src/retrieval/utils.h b/src/retrieval/utils.h
index b99bf64..d773220 100644
--- a/src/retrieval/utils.h
+++ b/src/retrieval/utils.h
@@ -52,7 +52,8 @@ struct ImageScore {
 template <int N, int kSigma = 16>
 class HammingDistWeightFunctor {
  public:
-  static const size_t kMaxHammingDistance = static_cast<size_t>(1.5f * kSigma);
+  // static const size_t kMaxHammingDistance = static_cast<size_t>(1.5f * kSigma);
+  static const size_t kMaxHammingDistance = 24;
 
   HammingDistWeightFunctor() {
     // Fills the look-up table.
(END)
```
#### 3.2 编辑CmakeList.txt
set(Boost_DEBUG ON)，打开boost的调试信息，boost的链接最容易出问题。(以下的内容仅供了解，无需修改)
**主要注意:** -DBoost_USE_STATIC_RUNTIME=ON 这个设置是指boost的库在使用cpp的runtime时候将会使用静态库，如果这个选项打开了，则需要往CmakeList.txt(colmap的根目录)中添加：
```sh
# set the used type of runtime lib to be static
set(CMAKE_CXX_FLAGS_RELEASE "/MT")
set(CMAKE_CXX_FLAGS_DEBUG "/MTd")
```
上面意味着运行时库调用时选择静态运行时库(vs中，在项目->cpp->代码生成中有MT/MD的配置), 而且对应的编译出来的boost库，编译时需要带上： --link=static --runtime-link=static --build-type=complete 参数;
### 3.3 编译执行：
注意我们使用静态的boost避免boost 的链接错误；
```sh
python scripts/python/build.py \
    --build_path "F:/prjs/colmap-3.6/build" \
    --colmap_path "F:/prjs/colmap-3.6" \
    --boost_path "F:/BASE_ENV/forOpenMVS/boost_1_73_0_v140" \
    --boost_include_dir "F:/BASE_ENV/forOpenMVS/boost_1_73_0_v140" \
    --boost_lib_dir "F:/BASE_ENV/forOpenMVS/boost_1_73_0_v140\lib64-msvc-14.0" \
    --qt_path "F:/BASE_ENV/forOpenMVS/qt_msvc2015_64/msvc2015_64" \
    --cgal_path "F:/BASE_ENV/forOpenMVS/CGAL-5.1/build" \
    --cmake_generator "Visual Studio 14" \
    --with_cuda \
    --cuda_path "C:/Program Files/NVIDIA GPU Computing Toolkit/CUDA/v10.2" \
```
上述命令会失败，但是没关系，用code打开F:/prjs/colmap-3.6/build/colmap/__build__：
全局替换的方式删除： BOOST_ALL_DYN_LINK=1，
然后在F:/prjs/colmap-3.6/build/colmap/__build__里找到COLMAP.sln，然后手动用vs打开然后编译；
推荐使用VS2015的工具对colmap进行编译.
### 4 给出我编译后的库目录结构（最重要的是__install__/lib下面的内容）：
其中： __install__/lib下面的platform中必须要有qwindows.dll，参考问题4。
然后： __install__/lib里面的cgal*.dll也是不必须的，因为本博客使用的cgal是5.x，5.x的cgal都是header only 的库，所以该dll可以没有，但是其他的dll像是libgmp-10.dll确是必要的，否则将无法运行。
```log
sagar@DESKTOP-QM75KNS MINGW64 /f/prjs/colmap-3.6/build
$ ls
__download__  ceres-solver              colmap  freeimage  glew  suite-sparse
__install__   CGAL-vc140-mt-4.14.3.dll  eigen   gflags     glog
sagar@DESKTOP-QM75KNS MINGW64 /f/prjs/colmap-3.6/build
$ ls __download__/
ceres-solver-1.14.0.zip  freeimage-3.18.0.zip  glew-2.1.0.zip  suite-sparse.zip
eigen-3.3.7.zip          gflags-2.2.2.zip      glog-0.3.5.zip
sagar@DESKTOP-QM75KNS MINGW64 /f/prjs/colmap-3.6/build
$ ls
__download__  ceres-solver              colmap  freeimage  glew  suite-sparse
__install__   CGAL-vc140-mt-4.14.3.dll  eigen   gflags     glog
sagar@DESKTOP-QM75KNS MINGW64 /f/prjs/colmap-3.6/build
$ cd __install__/lib
sagar@DESKTOP-QM75KNS MINGW64 /f/prjs/colmap-3.6/build/__install__/lib
$ tree
.
├── FreeImage.dll
├── FreeImage.lib
├── Qt5Core.dll
├── Qt5Gui.dll
├── Qt5Widgets.dll
├── ceres.lib
├── cmake
│   ├── gflags
│   │   ├── gflags-config-version.cmake
│   │   ├── gflags-config.cmake
│   │   ├── gflags-nonamespace-targets-release.cmake
│   │   ├── gflags-nonamespace-targets.cmake
│   │   ├── gflags-targets-release.cmake
│   │   └── gflags-targets.cmake
│   ├── glew
│   │   ├── CopyImportedTargetProperties.cmake
│   │   ├── glew-config.cmake
│   │   ├── glew-targets-release.cmake
│   │   └── glew-targets.cmake
│   ├── glog
│   │   ├── glog-config-version.cmake
│   │   ├── glog-config.cmake
│   │   ├── glog-targets-release.cmake
│   │   └── glog-targets.cmake
│   └── suitesparse-4.5.0
│       ├── SuiteSparse-targets-release.cmake
│       ├── SuiteSparse-targets.cmake
│       ├── suitesparse-config-version.cmake
│       └── suitesparse-config.cmake
├── colmap
│   ├── colmap.lib
│   ├── colmap_cuda.lib
│   ├── flann.lib
│   ├── graclus.lib
│   ├── lsd.lib
│   ├── pba.lib
│   ├── poisson_recon.lib
│   ├── sift_gpu.lib
│   ├── sqlite3.lib
│   └── vlfeat.lib
├── cudart64_102.dll
├── gflags_nothreads_static.lib
├── gflags_static.lib
├── glew32.dll
├── glew32.lib
├── glog.lib
├── libamd.lib
├── libblas.dll
├── libbtf.lib
├── libcamd.lib
├── libccolamd.lib
├── libcholmod.lib
├── libcolamd.lib
├── libcxsparse.lib
├── libgcc_s_sjlj-1.dll
├── libgfortran-3.dll
├── libglew32.lib
├── libgmp-10.dll
├── libklu.lib
├── liblapack.dll
├── libldl.lib
├── libquadmath-0.dll
├── libspqr.lib
├── libumfpack.lib
├── metis.lib
├── pkgconfig
│   └── glew.pc
├── platforms
│   └── qwindows.dll
└── suitesparseconfig.lib
8 directories, 62 files
```
### 5 可能遇到的问题：
- Q 1 一切都能正常编译通过，但是出现“程序无法正常启动, 0xc000007b”
- **解决方案：** 仔细核对我提供的目录，看看是否是dll少了，一般libgmp-10.dll少了就会报这个错误，可以参照问题4
- Q 2 boost总是报link2005的重定义错误：
- **解决方案：** 打开colmap.sln，你会发现： 项目->属性c++预处理(宏定义) 中多了BOOST_ALL_DYN_LINK=1，用如下方法全局删除即可：用code打开F:/prjs/colmap-3.6/build/colmap/__build__：
全局替换的方式删除： BOOST_ALL_DYN_LINK=1，然后vs会让你重载项目配置，再次编译应该可以直接通过。造成的原因可能是boost总是默认enable了autolink，这导致你必须把你的boost库的版本和你的vs版本对上，而且可能默认是全部动态链接（即使你配置了静态链接以后），可能的解决方案是，在项目根目录下面的CMAKELIST.txt中添加: 
- Q 3 libcpmt.lib(ppltasks.obj) : error LNK2001: 无法解析的外部符号 __CxxFrameHandler4报错：
- **解决方案：** 是因为你的库用的是vs2019编译的，然后colmap又用vs2015编译，就会报这个错误。
- Q 4 Qt platform plugin 'windows' not found
- **解决方案：** 是因为你虽然安装了qt，但是没有复制相关的dll到./build/colmap/__install__/lib下（colmap的运行直接双击__install__/COLMAP.BAT即可），复制方案：(也就是build.py中的编译后处理部分做的事情)
```py
def build_post_process(args):
    if PLATFORM_IS_WINDOWS:
        lapack_paths = glob.glob(
            os.path.join(args.install_path, "lib64/lapack_blas_windows/*.dll"))
        if lapack_paths:
            for lapack_path in lapack_paths:
                copy_file_if_not_exists(
                    lapack_path,
                    os.path.join(
                        args.install_path, "lib",
                        os.path.basename(lapack_path)))
        if args.qt_path:
            copy_file_if_not_exists(
                os.path.join(args.qt_path, "bin/Qt5Core.dll"),
                os.path.join(args.install_path, "lib/Qt5Core.dll"))
            copy_file_if_not_exists(
                os.path.join(args.qt_path, "bin/Qt5Gui.dll"),
                os.path.join(args.install_path, "lib/Qt5Gui.dll"))
            copy_file_if_not_exists(
                os.path.join(args.qt_path, "bin/Qt5Widgets.dll"),
                os.path.join(args.install_path, "lib/Qt5Widgets.dll"))
            mkdir_if_not_exists(
                os.path.join(args.install_path, "lib/platforms"))
            copy_file_if_not_exists(
                os.path.join(args.qt_path, "plugins/platforms/qwindows.dll"),
                os.path.join(args.install_path, "lib/platforms/qwindows.dll"))
        if args.with_cuda and args.cuda_path:
            cudart_lib_path = glob.glob(os.path.join(args.cuda_path,
                                                     "bin/cudart64_*.dll"))[0]
            copy_file_if_not_exists(
                cudart_lib_path,
                os.path.join(args.install_path, "lib",
                             os.path.basename(cudart_lib_path)))
        if args.cgal_path:
            gmp_lib_path = os.path.join(
                args.cgal_path, "auxiliary/gmp/lib/libgmp-10.dll")
            if os.path.exists(gmp_lib_path):
                copy_file_if_not_exists(
                    gmp_lib_path,
                    os.path.join(args.install_path, "lib/libgmp-10.dll"))
            cgal_lib_path = glob.glob(os.path.join(
                args.cgal_path, "bin/CGAL-vc*-mt-*.dll"))
            copy_file_if_not_exists(
                cgal_lib_path[0],
                os.path.join(args.install_path, "lib",
                    os.path.basename(cgal_lib_path[0])))
```
- Q 5 莫名其妙报了cuda的编译的错误：error : identifier "__floorf" is undefined in device code
- **解决方案：** vs2019 16.9.3以及以上有这个问题，你需要卸载然后回退到16.8.5
- Q 6 C2132 编译器错误：表达式的计算结果不是常数
- **解决方案：** 可能是你的编译器对cpp的新特性支持的不够好？，修改 src/retrieval/utils.h 的 55行为：
```
  // static const size_t kMaxHammingDistance = static_cast<size_t>(1.5f * kSigma);
  static const size_t kMaxHammingDistance = static_cast<size_t>(24);
```
## 2020/05/19
### osg模型调整光照以及模型闪烁问题[z-lighting]
### 0 模型闪烁原因推测
- 1 关于模型闪烁的问题，很可能是由于坐标的值的有效位数超过了7位，目前的opengl的gpu渲染（老一点的显卡以及gl）都是以单精度来渲染点的位置的，所以如果坐标很大，很可能导致单精度无法精确表示有效位数超过7位的数据，然后发生截断。
- 2 关于z-lighting的问题，尝试了网上大多数的方法：可以使用osg封装的polygonOffset来避免重叠面片交替出现的问题，当然最好的方案是找的模型本身重叠面片就少
### 1 meshlab手动调模型
filters->Normals,curve,orientations->transform...
### 2 使用osg降低模型的点的坐标大小
```cpp
	osg::Vec3f center1 = TerrainM1->getBound().center();
	float radius1 = TerrainM1->getBound().radius();
	osg::Vec3f center2 = TerrainM2->getBound().center();
	float radius2 = TerrainM2->getBound().radius();
	TerrainM1->setMatrix(
		osg::Matrix::translate(-center1.x(), -center1.y(), -center1.z()) *
		osg::Matrix::rotate(osg::DegreesToRadians(180.0), 1, 0, 0) *
		osg::Matrix::translate(center1.x(), center1.y(), center1.z()) *
		osg::Matrix::translate(0, 0, radius2 * 0.80 + radius1)
	);
	
	// to modify the model's points render value
	mRoot->getChild(0)->asTransform()->asMatrixTransform()->setMatrix(
		osg::Matrix::translate(-center1.x(), -center1.y(), -center1.z())
	);
	osgDB::writeNodeFile(*(mRoot->getChild(0)->asNode()), "sc.obj");
```
### 3 关于材质，光照，以及模型读写旋转平移的例子
关于材料的颜色光照等可以参考[https://learnopengl-cn.readthedocs.io/zh/latest/02%20Lighting/03%20Materials/](https://learnopengl-cn.readthedocs.io/zh/latest/02%20Lighting/03%20Materials/)
```cpp
  // mRoot是一个osg::ref_ptr<osg::Group>
	auto TerrainM1 = new osg::MatrixTransform;
	auto terrain1 = new osg::PositionAttitudeTransform;
	auto TerrainM2 = new osg::MatrixTransform;
	auto terrain2 = new osg::PositionAttitudeTransform;
	osgDB::Options  *a = new osgDB::Options(std::string("noRotation")); // 关掉模型优化绘制(OSG在加载obj模型的时候，会默认将模型绕x轴逆时针旋转90度,此处设置不旋转)
	// setting material
	osg::Material *material = new osg::Material;
	material->setDiffuse(osg::Material::FRONT, osg::Vec4(0.75, 0.80, 0.75, 1.0));
	material->setAmbient(osg::Material::FRONT, osg::Vec4(0.75, 0.80, 0.75, 1.0));
	// material->setShininess(osg::Material::FRONT, 90.0);
	
	// turn off light effect
	auto Model1 = osgDB::readNodeFile(part1Path, a);
	auto pState1 = Model1->getOrCreateStateSet();
	pState1->setMode(GL_LIGHTING, osg::StateAttribute::ON);
	pState1->setAttribute(material);
	// pState1->setMode(GL_DEPTH_TEST, osg::StateAttribute::OFF | osg::StateAttribute::OVERRIDE);
    // pState1->setRenderingHint(osg::StateSet::TRANSPARENT_BIN);
    // set polygon offset
	osg::ref_ptr<osg::PolygonOffset> polyOff = new osg::PolygonOffset();
	float mFactor = 1.0, mUnits = 1.0;
	polyOff->setFactor(mFactor);
	polyOff->setUnits(mUnits);
	pState1->setAttributeAndModes(new osg::PolygonOffset(-1.0f,-1.0f),osg::StateAttribute::ON);
	material->setEmission(osg::Material::FRONT, osg::Vec4(0.75, 0.80, 0.75, 1.0));
	// pState1->setAttributeAndModes(polyOff.get(), osg::StateAttribute::ON | osg::StateAttribute::OVERRIDE);
	// auto pGeom1 = Model1->asGeode()->asGeometry();
	// pGeom1->getOrCreateStateSet()->setMode(GL_NV_framebuffer_multisample_coverage, osg::StateAttribute::ON | osg::StateAttribute::PROTECTED | osg::StateAttribute::OVERRIDE);
	TerrainM1->addChild(Model1);
	TerrainM1->setName(modelPrefix + "1");
	auto Model2 = osgDB::readNodeFile(part2Path, a);
	auto pState2 = Model2->getOrCreateStateSet();
	pState2->setMode(GL_LIGHTING, osg::StateAttribute::ON);
	pState2->setAttribute(material);
	
	pState2->setMode(GL_BLEND, osg::StateAttribute::ON);
	TerrainM2->addChild(Model2);
	TerrainM2->setName(modelPrefix + "2");
	
	// rotate to make sure the building is standing on the ground
	osg::Vec3f center1 = TerrainM1->getBound().center();
	float radius1 = TerrainM1->getBound().radius();
	osg::Vec3f center2 = TerrainM2->getBound().center();
	float radius2 = TerrainM2->getBound().radius();
	TerrainM1->setMatrix(
		osg::Matrix::translate(-center1.x(), -center1.y(), -center1.z()) *
		osg::Matrix::rotate(osg::DegreesToRadians(180.0), 1, 0, 0) *
		osg::Matrix::translate(center1.x(), center1.y(), center1.z()) *
		osg::Matrix::translate(0, 0, radius2 * 0.80 + radius1)
	);
	mRoot->addChild(TerrainM1);
	TerrainM2->setMatrix(
		osg::Matrix::translate(-center2.x(), -center2.y(), -center2.z()) *
		osg::Matrix::rotate(osg::DegreesToRadians(180.0), 1, 0, 0) *
		osg::Matrix::translate(center2.x(), center2.y(), center2.z()) *
		osg::Matrix::translate(0, 0, 0.5 * radius2)
	);
	mRoot->addChild(TerrainM2);
	// to modify the model's points render value
	mRoot->getChild(0)->asTransform()->asMatrixTransform()->setMatrix(
		osg::Matrix::translate(-center1.x(), -center1.y(), -center1.z())
	);
	mRoot->getChild(1)->asTransform()->asMatrixTransform()->setMatrix(
		osg::Matrix::translate(-center1.x(), -center1.y(), -center1.z())
	);
	mRoot->getChild(4)->asTransform()->asMatrixTransform()->setMatrix(
		osg::Matrix::translate(-center1.x(), -center1.y(), -center1.z())
	);
	mRoot->getChild(5)->asTransform()->asMatrixTransform()->setMatrix(
		osg::Matrix::translate(-center1.x(), -center1.y(), -center1.z())
	);
	osgDB::writeNodeFile(*(mRoot->getChild(0)->asNode()), "sc.obj");
	osgDB::writeNodeFile(*(mRoot->getChild(1)->asNode()), "de.obj");
	osgDB::writeNodeFile(*(mRoot->getChild(4)->asNode()), "par1.obj");
	osgDB::writeNodeFile(*(mRoot->getChild(5)->asNode()), "par2.obj");
```
## 2020/05/19
### 1 编译orb_slam
```sh
git clone https://github.com/UZ-SLAMLab/ORB_SLAM3.git ORB_SLAM3
```
建议编译前，先看一下该项目上的一个pull request:(使用原来项目问题过多, 遇到的每一个问题在第4节都会详细描述，于是使用如下的一个PR)
[https://github.com/UZ-SLAMLab/ORB_SLAM3/pull/53](https://github.com/UZ-SLAMLab/ORB_SLAM3/pull/53)
推荐使用vs2015生成器;
### 2 编译
#### 2.1 DBoW2 编译(如果使用pr，本步骤可以不看，2.3的orbslam3也对所有cmakelist.txt的修改做了说明)
主要是需要添加oepncv和boost的依赖
```diff
PS F:\prjs\ORB_SLAM3> git diff
diff --git a/Thirdparty/DBoW2/CMakeLists.txt b/Thirdparty/DBoW2/CMakeLists.txt
index c561724..2368c23 100644
--- a/Thirdparty/DBoW2/CMakeLists.txt
+++ b/Thirdparty/DBoW2/CMakeLists.txt
@@ -32,9 +32,22 @@ if(NOT OpenCV_FOUND)
    endif()
 endif()
+
+set(Boost_USE_STATIC_LIBS ON)
+add_definitions("-DBOOST_ALL_NO_LIB=1")
+find_package(Boost REQUIRED COMPONENTS
+             serialization)
+
 set(LIBRARY_OUTPUT_PATH ${PROJECT_SOURCE_DIR}/lib)
-include_directories(${OpenCV_INCLUDE_DIRS})
+include_directories(${OpenCV_INCLUDE_DIRS} ${BOOST_INCLUDEDIR})
+link_directories(${Boost_LIBRARY_DIRS})
+
+message("lib is: " ${Boost_SERIALIZATION_LIBRARY})
+
 add_library(DBoW2 SHARED ${SRCS_DBOW2} ${SRCS_DUTILS})
-target_link_libraries(DBoW2 ${OpenCV_LIBS})
+target_link_libraries(DBoW2 
+    ${OpenCV_LIBS}    
+    ${Boost_SERIALIZATION_LIBRARY}
+)
diff --git a/Thirdparty/DBoW2/DBoW2/FORB.cpp b/Thirdparty/DBoW2/DBoW2/FORB.cpp
index 1f1990c..80bf473 100644
--- a/Thirdparty/DBoW2/DBoW2/FORB.cpp
+++ b/Thirdparty/DBoW2/DBoW2/FORB.cpp
@@ -13,7 +13,7 @@
 #include <vector>
 #include <string>
 #include <sstream>
-#include <stdint-gcc.h>
+#include <stdint.h>
 #include "FORB.h"
```
如果指定了vs2019，然后又用vs2015编译的库，就需要用如下的最后一个参数去掉boost的autolink;
```sh
mkdir build && cd build
cmake .. \
-G "Visual Studio 16" \
-DCMAKE_BUILDY_TYPE=Release \
-DOpenCV_DIR="F:/BASE_ENV/forOpenMVS/opencv/build" \
-DBOOST_ROOT="F:/BASE_ENV/forOpenMVS/boost_1_73_0_v140" \
-DBOOST_INCLUDEDIR="F:/BASE_ENV/forOpenMVS/boost_1_73_0_v140" \
-DBOOST_LIBRARYDIR="F:/BASE_ENV/forOpenMVS/boost_1_73_0_v140" \
-DBOOST_ALL_NO_LIB=1 \     # 避免boost的autolink，autolink会要求vs版本和boost版本一致
```
### 2.2 g2o
项目->属性->c++->预处器宏定义->添加： WINDOWS，否则会出现vasprintf找不到定义。
```sh
cd ../../g2o
echo "Configuring and building Thirdparty/g2o ..."
mkdir build
cd build
cmake .. \
-G "Visual Studio 14" \
-DCMAKE_BUILDY_TYPE=Release \
-DEIGEN3_INCLUDE_DIR="F:\BASE_ENV\forOpenMVS\eigen" \
-DBOOST_ALL_NO_LIB=1 \
```
### 2.3 orbslam3
#### 2.3.0 首先按照下面的diff修改所有的internal::axpy和internal::atxpy
```
```
如果你是自己在orbslam3直接编译的话，请参考: [https://github.com/RainerKuemmerle/g2o/issues/91](https://github.com/RainerKuemmerle/g2o/issues/91)
#### 2.3.1 找不到unistd.h
首先：unistd.h需要修改调，主要是为了使用usleep，该函数使用如下代码替换：
```cpp
```cpp
#include <windows.h>
void usleep(__int64 usec) 
{ 
    HANDLE timer; 
    LARGE_INTEGER ft; 
    ft.QuadPart = -(10*usec); // Convert to 100 nanosecond interval, negative value indicates relative time
    timer = CreateWaitableTimer(NULL, TRUE, NULL); 
    SetWaitableTimer(timer, &ft, 0, NULL, NULL, 0); 
    WaitForSingleObject(timer, INFINITE); 
    CloseHandle(timer); 
}
```
或者如下一行能搞定：**推荐这个方法**
```cpp
            if (ttrack < T) {
                long usec = static_cast<long>((T - ttrack) * 1e6);
                std::this_thread::sleep_for(std::chrono::microseconds(usec));
            }
```
#### 2.3.2 使用cmake-gui开始编译
cmake-gui配置：
opencv，boost，需要修改cmakelist.txt:
添加如下定义：
```cmake
-DBOOST_ALL_NO_LIB=1
```
**如下是我对cmakeList.txt做出的修改。**
```diff
diff --git a/CMakeLists.txt b/CMakeLists.txt
index 70d03fe..79b32e7 100644
--- a/CMakeLists.txt
+++ b/CMakeLists.txt
@@ -34,6 +34,7 @@ if (CMAKE_CXX_COMPILER_ID MATCHES "MSVC")
   #set(CMAKE_CXX_FLAGS_DEBUG "${CMAKE_CXX_FLAGS_DEBUG} /MTd")
 endif()
 
+add_definitions("-DBOOST_ALL_NO_LIB=1")
 
 LIST(APPEND CMAKE_MODULE_PATH ${PROJECT_SOURCE_DIR}/cmake_modules)
 
@@ -46,13 +47,15 @@ if(NOT OpenCV_FOUND)
 endif()
 MESSAGE(STATUS "OpenCV VERSION: ${OpenCV_VERSION}")
 
-find_package(Eigen3 3.1.0 REQUIRED)
+# find_package(Eigen3 REQUIRED)
+set(EIGEN3_INCLUDE_DIR "F:/BASE_ENV/forOpenMVS/eigen")
+MESSAGE("eigen & boost inlcude dir is: @@@@@@" ${EIGEN3_INCLUDE_DIRS}) 
 
 find_package(Pangolin REQUIRED)
 find_package(realsense2)
 
 find_package(Boost REQUIRED COMPONENTS serialization)
-MESSAGE(STATUS "Boost_LIBRARIES: ${Boost_LIBRARIES}")
+MESSAGE(STATUS "cxy@@@@@@@@@@ Boost_INCLUDE_DIRS & Boost_LIBRARIES: ${Boost_INCLUDE_DIRS} ${Boost_LIBRARIES}")
 
 set(OPENSSL_USE_STATIC_LIBS TRUE)
 find_package(OpenSSL REQUIRED) # for crypto library
@@ -65,6 +68,7 @@ include_directories(
   ${EIGEN3_INCLUDE_DIR}
   ${Pangolin_INCLUDE_DIRS}
   ${OPENSSL_INCLUDE_DIR}
+  ${Boost_INCLUDE_DIRS}
 )
 
 set(CMAKE_ARCHIVE_OUTPUT_DIRECTORY ${PROJECT_SOURCE_DIR}/lib)
diff --git a/Thirdparty/DBoW2/CMakeLists.txt b/Thirdparty/DBoW2/CMakeLists.txt
index bf987be..e527175 100644
--- a/Thirdparty/DBoW2/CMakeLists.txt
+++ b/Thirdparty/DBoW2/CMakeLists.txt
@@ -51,10 +51,16 @@ if(NOT OpenCV_FOUND)
   endif()
 endif()
 MESSAGE(STATUS "OpenCV VERSION: ${OpenCV_VERSION}")
-include_directories(${OpenCV_INCLUDE_DIRS})
-target_link_libraries(DBoW2 ${OpenCV_LIBS})
 
 # add Boost
-find_package(Boost REQUIRED COMPONENTS serialization)
-message(STATUS "Boost_LIBRARIES: ${Boost_LIBRARIES}")
-target_link_libraries(DBoW2 ${Boost_LIBRARIES})
+set(Boost_USE_STATIC_LIBS ON)
+add_definitions("-DBOOST_ALL_NO_LIB=1")
+find_package(Boost REQUIRED COMPONENTS 
+                  serialization)
+message(STATUS "cxy@@@@@@@@ Boost_INCLUDE_DIRS & libs: ${Boost_INCLUDE_DIRS} >>>> ${Boost_LIBRARIES}")
+
+include_directories(${OpenCV_INCLUDE_DIRS} ${BOOST_INCLUDEDIR})
+target_link_libraries(DBoW2 
+  ${OpenCV_LIBS} 
+  ${Boost_LIBRARIES}
+)
diff --git a/Thirdparty/g2o/g2o/core/sparse_block_matrix.hpp b/Thirdparty/g2o/g2o/core/sparse_block_matrix.hpp
index 8dfa99c..80e4fa8 100644
--- a/Thirdparty/g2o/g2o/core/sparse_block_matrix.hpp
+++ b/Thirdparty/g2o/g2o/core/sparse_block_matrix.hpp
@@ -24,6 +24,13 @@
 // NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
 // SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
 
+// add these marcos to fix:  
+// 1>f:\prjs\orb_slam3\thirdparty\g2o\g2o\core\sparse_block_matrix.hpp(277): fatal error C1001: 编译器中发生内部错误。
+
+#define _AXPY(MatrixType,A,x,xoff,y,yoff)y.segment<MatrixType::RowsAtCompileTime>(yoff) += (A) * (x).segment<MatrixType::ColsAtCompileTime>(xoff)
+#define _ATXPY(MatrixType,A,x,xoff,y,yoff)y.segment<MatrixType::ColsAtCompileTime>(yoff) += (A).transpose() * (x).segment<MatrixType::RowsAtCompileTime>(xoff)
+
+
 namespace g2o {
   using namespace Eigen;
 
@@ -249,7 +256,8 @@ namespace g2o {
         const typename SparseBlockMatrix<MatrixType>::SparseMatrixBlock* a=it->second;
         int destOffset = it->first ? _rowBlockIndices[it->first - 1] : 0;
         // destVec += *a * srcVec (according to the sub-vector parts)
-        internal::axpy(*a, srcVec, srcOffset, destVec, destOffset);
+        // internal::axpy(*a, srcVec, srcOffset, destVec, destOffset);
+        _AXPY(MatrixType, *a, srcVec, srcOffset, destVec, destOffset);
       }
     }
   }
@@ -274,9 +282,12 @@ namespace g2o {
         if (destOffset > srcOffset) // only upper triangle
           break;
         // destVec += *a * srcVec (according to the sub-vector parts)
-        internal::axpy(*a, srcVec, srcOffset, destVec, destOffset);
-        if (destOffset < srcOffset)
-          internal::atxpy(*a, srcVec, destOffset, destVec, srcOffset);
+        // internal::axpy(*a, srcVec, srcOffset, destVec, destOffset);
+        _AXPY(MatrixType, *a, srcVec, srcOffset, destVec, destOffset);
+        if (destOffset < srcOffset) {
+          // internal::atxpy(*a, srcVec, destOffset, destVec, srcOffset);
+          _ATXPY(MatrixType, *a, srcVec, destOffset, destVec, srcOffset);
+        }
       }
     }
   }
@@ -305,7 +316,8 @@ namespace g2o {
         const typename SparseBlockMatrix<MatrixType>::SparseMatrixBlock* a=it->second;
         int srcOffset = rowBaseOfBlock(it->first);
         // destVec += *a.transpose() * srcVec (according to the sub-vector parts)
-        internal::atxpy(*a, srcVec, srcOffset, destVec, destOffset);
+        // internal::atxpy(*a, srcVec, srcOffset, destVec, destOffset);
+	    _ATXPY(MatrixType, *a, srcVec, srcOffset, destVec, destOffset);
       }
     }
     
diff --git a/Thirdparty/g2o/g2o/core/sparse_block_matrix_ccs.h b/Thirdparty/g2o/g2o/core/sparse_block_matrix_ccs.h
index 36ddfe6..91832cd 100644
--- a/Thirdparty/g2o/g2o/core/sparse_block_matrix_ccs.h
+++ b/Thirdparty/g2o/g2o/core/sparse_block_matrix_ccs.h
@@ -24,6 +24,9 @@
 // NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
 // SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
 
+#define _AXPY(MatrixType,A,x,xoff,y,yoff)y.segment<MatrixType::RowsAtCompileTime>(yoff) += (A) * (x).segment<MatrixType::ColsAtCompileTime>(xoff)
+#define _ATXPY(MatrixType,A,x,xoff,y,yoff)y.segment<MatrixType::ColsAtCompileTime>(yoff) += (A).transpose() * (x).segment<MatrixType::RowsAtCompileTime>(xoff)
+
 #ifndef G2O_SPARSE_BLOCK_MATRIX_CCS_H
 #define G2O_SPARSE_BLOCK_MATRIX_CCS_H
 
@@ -122,7 +125,8 @@ namespace g2o {
             const SparseMatrixBlock* a = it->block;
             int srcOffset = rowBaseOfBlock(it->row);
             // destVec += *a.transpose() * srcVec (according to the sub-vector parts)
-            internal::atxpy(*a, srcVec, srcOffset, destVec, destOffset);
+            // internal::atxpy(*a, srcVec, srcOffset, destVec, destOffset);
+            _ATXPY(MatrixType, *a, srcVec, srcOffset, destVec, destOffset);
           }
         }
       }
diff --git a/Thirdparty/g2o/g2o/core/sparse_block_matrix_diagonal.h b/Thirdparty/g2o/g2o/core/sparse_block_matrix_diagonal.h
index 7b13b9f..8605a5f 100644
--- a/Thirdparty/g2o/g2o/core/sparse_block_matrix_diagonal.h
+++ b/Thirdparty/g2o/g2o/core/sparse_block_matrix_diagonal.h
@@ -24,6 +24,9 @@
 // NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
 // SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
 
+#define _AXPY(MatrixType,A,x,xoff,y,yoff)y.segment<MatrixType::RowsAtCompileTime>(yoff) += (A) * (x).segment<MatrixType::ColsAtCompileTime>(xoff)
+#define _ATXPY(MatrixType,A,x,xoff,y,yoff)y.segment<MatrixType::ColsAtCompileTime>(yoff) += (A).transpose() * (x).segment<MatrixType::RowsAtCompileTime>(xoff)
+
 #ifndef G2O_SPARSE_BLOCK_MATRIX_DIAGONAL_H
 #define G2O_SPARSE_BLOCK_MATRIX_DIAGONAL_H
 
@@ -94,7 +97,8 @@ namespace g2o {
           int srcOffset = destOffset;
           const SparseMatrixBlock& A = _diagonal[i];
           // destVec += *A.transpose() * srcVec (according to the sub-vector parts)
-          internal::axpy(A, srcVec, srcOffset, destVec, destOffset);
+          // internal::axpy(A, srcVec, srcOffset, destVec, destOffset);
+          _AXPY(MatrixType, A, srcVec, srcOffset, destVec, destOffset);
         }
       }
 
```
### 3 编译成功显示：
```log
1>F:\prjs\ORB_SLAM3\Thirdparty\Pangolin\include\pangolin/gl/gldraw.h(109,1): warning C4267: “参数”: 从“size_t”转换到“GLint”，可能丢失数据
1>  正在创建库 F:/prjs/ORB_SLAM3_Fix/ORB_SLAM3/lib/mono_kitti.lib 和对象 F:/prjs/ORB_SLAM3_Fix/ORB_SLAM3/lib/mono_kitti.exp
1>mono_kitti.vcxproj -> F:\prjs\ORB_SLAM3_Fix\ORB_SLAM3\bin\mono_kitti.exe
1>已完成生成项目“mono_kitti.vcxproj”的操作。
========== 生成: 成功 1 个，失败 0 个，最新 4 个，跳过 0 个 ==========
```
  如下是一个调用gif：
  - 1 下载数据：[http://robotics.ethz.ch/~asl-datasets/ijrr_euroc_mav_dataset/machine_hall/MH_01_easy/MH_01_easy.zip](http://robotics.ethz.ch/~asl-datasets/ijrr_euroc_mav_dataset/machine_hall/MH_01_easy/MH_01_easy.zip)
- 2 进入：ORB_SLAM3/Examples，执行脚本euroc_eval_examles.sh中的一行，将其中的一行（比如第7行）改成你需要的格式，然后拿出来执行：
```sh
./Monocular/mono_euroc ../Vocabulary/ORBvoc.txt ./Monocular/EuRoC.yaml ./EuRoc_Data/MH_01_easy/ ./Monocular/EuRoC_TimeStamps/MH01.txt result/Resdataset-MH01_mono
```
执行结果： 
![https://cdn.jsdelivr.net/gh/xychen5/blogImgs@main/imgs/orbslam3.5qu5qjc1jvw0.gif](https://cdn.jsdelivr.net/gh/xychen5/blogImgs@main/imgs/orbslam3.5qu5qjc1jvw0.gif)
### 4 可能遇到的问题
#### 4.1 g2o -> vasprint 找不到标识符
到它的声明处，就会发现，它的声明和定义均位于非活动预处理器块中，被宏定义WINDOWS关闭了。所以添加对应的宏定义即可：右键项目->属性->C++->预处理器->预处理器定义，为其添加一个变量，WINDOWS，保存设定之后，这个错误也就消失了。
以上过程也可以在cmakelist.txt中添加： ADD_DEFINITIONS(-DWINDOWS)
#### 4.2 orb-slam3 -> cl.exe has no C++11 support.  Please use a different C++ compiler.
因为cmakelist对于cl的c++11的支持方式需要如下编写：
```cmake
--- a/CMakeLists.txt
+++ b/CMakeLists.txt
@@ -17,19 +17,20 @@ set(CMAKE_CXX_FLAGS_RELEASE "${CMAKE_CXX_FLAGS_RELEASE} -march=native")
 
 # Check C++11 or C++0x support
 include(CheckCXXCompilerFlag)
-CHECK_CXX_COMPILER_FLAG("-std=c++11" COMPILER_SUPPORTS_CXX11)
-CHECK_CXX_COMPILER_FLAG("-std=c++0x" COMPILER_SUPPORTS_CXX0X)
-if(COMPILER_SUPPORTS_CXX11)
-   set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -std=c++11")
-   add_definitions(-DCOMPILEDWITHC11)
-   message(STATUS "Using flag -std=c++11.")
-elseif(COMPILER_SUPPORTS_CXX0X)
-   set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -std=c++0x")
-   add_definitions(-DCOMPILEDWITHC0X)
-   message(STATUS "Using flag -std=c++0x.")
-else()
-   message(FATAL_ERROR "The compiler ${CMAKE_CXX_COMPILER} has no C++11 support. Please use a different C++ compiler.")
-endif()
+set (CMAKE_CXX_STANDARD 11)
+# CHECK_CXX_COMPILER_FLAG("-std=c++11" COMPILER_SUPPORTS_CXX11)
+# CHECK_CXX_COMPILER_FLAG("-std=c++0x" COMPILER_SUPPORTS_CXX0X)
+# if(COMPILER_SUPPORTS_CXX11)
+#    set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -std=c++11")
+#    add_definitions(-DCOMPILEDWITHC11)
+#    message(STATUS "Using flag -std=c++11.")
+# elseif(COMPILER_SUPPORTS_CXX0X)
+#    set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -std=c++0x")
+#    add_definitions(-DCOMPILEDWITHC0X)
+#    message(STATUS "Using flag -std=c++0x.")
+# else()
+#    message(FATAL_ERROR "The compiler ${CMAKE_CXX_COMPILER} has no C++11 support. Please use a different C++ compiler.")
+# endif()
```
#### 4.3 stdio-gcc.h找不到
将其改为stdio.h即可
#### 4.4 Failed to run MSBuild command:      C:/Program Files (x86)/MSBuild/14.0/bin/MSBuild.exe  
将上述的MSBuild.exe添加到里面，然后[https://developer.microsoft.com/zh-cn/windows/downloads/sdk-archive/](https://developer.microsoft.com/zh-cn/windows/downloads/sdk-archive/)
里面找到win8.1的sdk，安装即可。
#### 4.5 fata_error: compiler internal error on msc1.cpp:1xxx编译器内部错误
和g2o/core/matrix_operation.h的代码有关系，参考如下修改：
[https://github.com/RainerKuemmerle/g2o/issues/91](https://github.com/RainerKuemmerle/g2o/issues/91)
[https://github.com/UZ-SLAMLab/ORB_SLAM3/pull/53](https://github.com/UZ-SLAMLab/ORB_SLAM3/pull/53)
#### 4.6 std::max找不到定义
添加： 
```
#include <algorithm>
```
#### 4.7 找不到openssl/md5.h
可以尝试安装strawberry-perl，里面有oepnssl的库，然后下载openssl的源码获得其include。
这里也有openssl编译好的链接库： [https://indy.fulgan.com/SSL/LinkLibs/](https://indy.fulgan.com/SSL/LinkLibs/)
我的下载地址为：[https://indy.fulgan.com/SSL/LinkLibs/openssl-1.0.2g-x64_86-win64_LinkLibs.zip](https://indy.fulgan.com/SSL/LinkLibs/openssl-1.0.2g-x64_86-win64_LinkLibs.zip)
配置完成后比如一些openssl的依赖就需要手动添加了：
F:\BASE_ENV\openSSL\openssl\include
F:\BASE_ENV\openSSL\openssl\lib\ssleay32.lib
F:\BASE_ENV\openSSL\openssl\lib\libeay32.lib
#### 4.8 link2005 error 将所有项目->属性->c++->代码生成->MD改成MT
```log
1>msvcprt.lib(MSVCP140.dll) : error LNK2005: "public: class std::basic_istream<char,struct std::char_traits<char> > & __cdecl std::basic_istream<char,struct std::char_traits<char> >::operator>>(double &)" (??5?$basic_istream@DU?$char_traits@D@std@@@std@@QEAAAEAV01@AEAN@Z) 已经在 pangolin.lib(widgets.obj) 中定义
1>msvcprt.lib(MSVCP140.dll) : error LNK2005: "public: virtual __cdecl std::basic_iostream<char,struct std::char_traits<char> >::~basic_iostream<char,struct std::char_traits<char> >(void)" (??1?$basic_iostream@DU?$char_traits@D@std@@@std@@UEAA@XZ) 已经在 ORB_SLAM3.lib(System.obj) 中定义
1>libcpmt.lib(locale0.obj) : error LNK2038: 检测到“RuntimeLibrary”的不匹配项: 值“MT_StaticRelease”不匹配值“MD_DynamicRelease”(stereo_euroc.obj 中)
1>libcpmt.lib(locale0.obj) : error LNK2005: "void __cdecl std::_Facet_Register(class std::_Facet_base *)" (?_Facet_Register@std@@YAXPEAV_Facet_base@1@@Z) 已经在 msv
```
#### 4.9 QT5找不到FindQT5.cmake
```cmake
# step1: 设置qt的安装位置
set(CMAKE_PREFIX_PATH "/opt/Qt/5.12.3/gcc_64") # windows下应该是msvc2015 或者之后的
# step2: 设置你需要的qt的库的dir
set(Qt5_DIR "${CMAKE_PREFIX_PATH}/lib/cmake/Qt5")
set(Qt5Widgets_DIR "${CMAKE_PREFIX_PATH}/lib/cmake/Qt5Widgets")
set(Qt5Network_DIR "${CMAKE_PREFIX_PATH}/lib/cmake/Qt5Network")
set(Qt5LinguistTools_DIR "${CMAKE_PREFIX_PATH}/lib/cmake/Qt5LinguistTools")
find_package(Qt5 COMPONENTS Widgets Network LinguistTools)
```
## 2021/06/01 - 
### 0 安装ROS
参考[https://blog.csdn.net/weixin_43563233/article/details/112238082](https://blog.csdn.net/weixin_43563233/article/details/112238082)
```
C:\Windows\System32\cmd.exe /k "C:\Program Files (x86)\Microsoft Visual Studio\2019\Community\Common7\Tools\VsDevCmd.bat" -arch=amd64 -host_arch=amd64&& set ChocolateyInstall=c:\opt\chocolatey&& c:\opt\ros\melodic\x64\setup.bat
————————————————
版权声明：本文为CSDN博主「Myliuxuwei」的原创文章，遵循CC 4.0 BY-SA版权协议，转载请附上原文出处链接及本声明。
原文链接：https://blog.csdn.net/weixin_43563233/article/details/112238082
```
qt/ material
### 1 制作数据集跑orbslam3
#### 1.1 标定相机
- 1 首先打印标定板：
去[https://github.com/opencv/opencv/blob/master/doc/pattern.png](https://github.com/opencv/opencv/blob/master/doc/pattern.png)下载
- 2 计算打印出来的标定板的真实长度
  - 2.1 首先用一图片查看软件打开，看看真个图片的宽所占的像素，是： 3410
  - 2.2 然后看看图片中横向的7个格子的宽度所占的像素，是：2841
  - 2.3 整张A4的宽度为2100.2mm
  - 2.4 所以你的格子宽度为： 249.965mm
- 3 拍一组标定照片，注意标定的照片的长宽不要旋转
- 4 用如下shell完成标定
```sh
# 生成图片
python .\scripts\sep.py .\cali1080p.mp4 .\caliPics\cali1080p\
# 标定
python .\scripts\cali.py .\caliPics\cali31080p\ png
```
标定结果：
- 0 cali
```
# python代码:
ret: 1.1223834441333873
internal matrix:
 [[1.95046109e+03 0.00000000e+00 9.81757313e+02]
 [0.00000000e+00 1.93409142e+03 5.35441541e+02]
 [0.00000000e+00 0.00000000e+00 1.00000000e+00]]
distortion cofficients:
 [[ 4.17901304e-01 -4.92447547e+00 -1.55811973e-04  7.83587527e-03
   1.82138290e+01]]
avg error: 0.1469
# matlab
```
#### 1.2 制作需要的数据集
将视频解帧然后形成csv列表，然后运行如下命令：
```
python .\scripts\sep.py ./workRoom2.mp4 ./viPics/workRoom2
python .\scripts\genIdx.py ./viPics/workRoom2 workRoom2.txt
./Monocular/mono_euroc ../Vocabulary/ORBvoc.txt ./data/myPhone1080p.yaml ./data/viPics/workRoom2 ./data/workRoom2.txt  ./data/resWorkRoom2
```
制作视频的一些技巧：
- 1 初始化先在原地待久一点
- 2 拐弯慢点
- 3 确保前后两帧能够有相同的特征点
#### 1.3 某些名词解释
IMU: inertial measurement unit，惯性测量单元
## draft
./Monocular/mono_euroc ../Vocabulary/ORBvoc.txt ./data/myPhone240p.yaml ./data/viPics/work3 ./data/work3.txt  ./data/resWork3
```
cd data
mkdir -p viPics/work4/mav0/cam0/data
python .\scripts\sep.py ./work4240p.mp4 ./viPics/work4/mav0/cam0/data
python .\scripts\genIdx.py ./viPics/work4 work4.txt
touch resWork4
cd ..
./Monocular/mono_euroc ../Vocabulary/ORBvoc.txt ./data/myPhone240p.yaml ./data/viPics/work4 ./data/work4.txt  ./data/resWork4
```
```
cd data
mkdir -p viPics/work5/mav0/cam0/data
python .\scripts\sep.py ./work5240p.mp4 ./viPics/work5/mav0/cam0/data
python .\scripts\genIdx.py ./viPics/work5/mav0/cam0/data work5.txt
touch resWork5
cd ..
./Monocular/mono_euroc ../Vocabulary/ORBvoc.txt ./data/myPhone240p.yaml ./data/viPics/work5 ./data/work5.txt  ./data/resWork5
```
```
cd data
mkdir -p viPics/work6/mav0/cam0/data
python .\scripts\sep.py ./work6240p.mp4 ./viPics/work6/mav0/cam0/data
python .\scripts\genIdx.py ./viPics/work6/mav0/cam0/data work6.txt
touch resWork6
cd ..
./Monocular/mono_euroc ../Vocabulary/ORBvoc.txt ./data/myPhone240p.yaml ./data/viPics/work6 ./data/work6.txt  ./data/resWork6
```
## 2020/06/06
### 1 osgQT的移植
首先参考官方项目：
[https://github.com/openscenegraph/osgQt](https://github.com/openscenegraph/osgQt)
这里先给出结果图：
![https://cdn.jsdelivr.net/gh/xychen5/blogImgs@main/imgs/gliderQT.1w4nlzuxphsw.png](https://cdn.jsdelivr.net/gh/xychen5/blogImgs@main/imgs/gliderQT.1w4nlzuxphsw.png)
#### 1.1 修改osgviewerqt.cpp如下： 这样你就能自己读模型了
```cpp
#include <osgQOpenGL/osgQOpenGLWidget>
#include <osgDB/ReadFile>
#include <osgUtil/Optimizer>
#include <osg/CoordinateSystemNode>
#include <osg/Switch>
#include <osg/Types>
#include <osgViewer/Viewer>
#include <osgText/Text>
#include <osgViewer/Viewer>
#include <osgViewer/ViewerEventHandlers>
#include <osgGA/TrackballManipulator>
#include <osgGA/FlightManipulator>
#include <osgGA/DriveManipulator>
#include <osgGA/KeySwitchMatrixManipulator>
#include <osgGA/StateSetManipulator>
#include <osgGA/AnimationPathManipulator>
#include <osgGA/TerrainManipulator>
#include <osgGA/SphericalManipulator>
#include <osgGA/Device>
#include <QApplication>
#include <QSurfaceFormat>
#include <iostream>
int main( int argc, char** argv )
{
    QSurfaceFormat format = QSurfaceFormat::defaultFormat();
#ifdef OSG_GL3_AVAILABLE
    format.setVersion(3, 2);
    format.setProfile(QSurfaceFormat::CoreProfile);
    format.setRenderableType(QSurfaceFormat::OpenGL);
    format.setOption(QSurfaceFormat::DebugContext);
#else
    format.setVersion(2, 0);
    format.setProfile(QSurfaceFormat::CompatibilityProfile);
    format.setRenderableType(QSurfaceFormat::OpenGL);
    format.setOption(QSurfaceFormat::DebugContext);
#endif
    format.setDepthBufferSize(24);
    //format.setAlphaBufferSize(8);
    format.setSamples(8);
    format.setStencilBufferSize(8);
    format.setSwapBehavior(QSurfaceFormat::DoubleBuffer);
    QSurfaceFormat::setDefaultFormat(format);
    QApplication app(argc, argv);
    // use an ArgumentParser object to manage the program arguments.
    osg::ArgumentParser arguments(&argc, argv);
    arguments.getApplicationUsage()->setApplicationName(
        arguments.getApplicationName());
    arguments.getApplicationUsage()->setDescription(arguments.getApplicationName() +
                                                    " is the standard OpenSceneGraph example which loads and visualises 3d models.");
    arguments.getApplicationUsage()->setCommandLineUsage(
        arguments.getApplicationName() + " [options] filename ...");
    arguments.getApplicationUsage()->addCommandLineOption("--image <filename>",
                                                          "Load an image and render it on a quad");
    arguments.getApplicationUsage()->addCommandLineOption("--dem <filename>",
                                                          "Load an image/DEM and render it on a HeightField");
    arguments.getApplicationUsage()->addCommandLineOption("--login <url> <username> <password>",
                                                          "Provide authentication information for http file access.");
    arguments.getApplicationUsage()->addCommandLineOption("-p <filename>",
                                                          "Play specified camera path animation file, previously saved with 'z' key.", 
                                                          "F:/dataSets/OpenSceneGraph-Data-3.4.0/OpenSceneGraph-Data/glider.osg");
    arguments.getApplicationUsage()->addCommandLineOption("--speed <factor>",
                                                          "Speed factor for animation playing (1 == normal speed).");
    arguments.getApplicationUsage()->addCommandLineOption("--device <device-name>",
                                                          "add named device to the viewer");
    osgQOpenGLWidget widget(&arguments);
    if (true) {
        osg::ref_ptr<osg::Node> loadedModel = osgDB::readNodeFile("F:/dataSets/OpenSceneGraph-Data-3.4.0/OpenSceneGraph-Data/glider.osg");
        if (!loadedModel)
        {
            std::cout << arguments.getApplicationName() << ": No data loaded" << std::endl;
            return 1;
        }
        // any option left unread are converted into errors to write out later.
        arguments.reportRemainingOptionsAsUnrecognized();
        // report any errors if they have occurred when parsing the program arguments.
        if (arguments.errors())
        {
            arguments.writeErrorMessages(std::cout);
            return 1;
        }
        widget.show();
        // optimize the scene graph, remove redundant nodes and state etc.
        osgUtil::Optimizer optimizer;
        optimizer.optimize(loadedModel);
        // mViewer = new osgViewer::Viewer();
        osg::ref_ptr<osgViewer::Viewer> mViewer = widget.getOsgViewer();
       
    		osg::ref_ptr<osg::Camera> camera = mViewer->getCamera();
        camera->setClearMask(GL_DEPTH_BUFFER_BIT | GL_COLOR_BUFFER_BIT);
        camera->setClearColor(osg::Vec4f(0.2f, 0.2f, 0.4f, 1.0f));
        // Add the Camera to the Viewer
        mViewer->setCamera(camera.get());
        // Add the Camera Manipulator to the Viewer
        // mViewer->setCameraManipulator(keyswitchManipulator.get());
        osg::ref_ptr<osgGA::TrackballManipulator> trackball = new osgGA::TrackballManipulator();
        mViewer->setCameraManipulator(trackball.get());
        mViewer->setSceneData(loadedModel);
        // // Realize the Viewer's graphics context, which already done in the default pWidget
        // mViewer->realize(); 
        return app.exec();
    }
}
```
#### 1.2 qt中使用
- 1 封装一个自己的类：
```cpp
#include <iostream>
#include <memory>
#include "osgHeaders.h"
/*
 * this class is mainly for initialize the pWidget
*/
class QOsgWidget {
public:
    // essential widget, use this ptr to be the real widget
    osgQOpenGLWidget* pWidget = nullptr;
    // QOsgWidget(QWidget* parent = nullptr);
    QOsgWidget(const std::string& modelPath, QWidget* parent = nullptr);
    ~QOsgWidget();
    // osg base vars
    osg::ref_ptr<osg::Group>                        mRoot                = nullptr;
    osg::ref_ptr<osg::Camera>                       camera               = nullptr;
    osg::ref_ptr<osgViewer::Viewer>                 mViewer              = nullptr;
    osg::ref_ptr<osgGA::TrackballManipulator>       trackball            = nullptr;
    osg::ref_ptr<osgGA::KeySwitchMatrixManipulator> keyswitchManipulator = nullptr;
    // for experiment:
    osg::ref_ptr<osgViewer::StatsHandler> pStat = nullptr;
    osg::ref_ptr<osgGA::TrackballManipulator> pTrackball = nullptr;
    osg::ref_ptr<osgViewer::Viewer> pmViewer = nullptr;
    // osg base funcs
    void InitManipulators();
    // load model into the mRoot
    void InitModel(const std::string& modelPathm, osg::ref_ptr<osg::Group>& mRoot);
    // init the cmaera
    void InitCameraConfig();
    osg::ref_ptr<osgViewer::Viewer> getViewer() { return mViewer; }
    // QObject::connect(&widget, &osgQOpenGLWidget::initialized);
};
```
- 2 调用这个类：
```cpp
            QOsgWidget *bBoxEdit = new QOsgWidget(modelPath, static_cast<QWidget*>(this));
            // use an ArgumentParser object to manage the program arguments.
            bBoxEdit->pWidget = new osgQOpenGLWidget(&arguments, this);
            bBoxEdit->pWidget->show();
            // init the manipulators
            bBoxEdit->InitManipulators();
            // init Scene Graph, that is to load the model
            bBoxEdit->InitModel(modelPath, bBoxEdit->mRoot);
            // init camera config
            bBoxEdit->InitCameraConfig();
            // 在这一行，将这个worksapceWidget添加到你想要添加的位置上就ok
            workspaceWidget = static_cast<QOpenGLWidget*>(&(*(bBoxEdit->pWidget))); 
```
### 2 关于内存申请位置不对带来的野指针问题
#### 2.1 问题描述：
```cpp
            resize(height() * 639 / 480, height());
            QOsgWidget *bBoxEdit = new QOsgWidget(modelPath, static_cast<QWidget*>(this));
            // use an ArgumentParser object to manage the program arguments.
            bBoxEdit->pWidget = new osgQOpenGLWidget(&arguments, this);
            bBoxEdit->pWidget->show();
            // init the manipulators
            bBoxEdit->InitManipulators();
            bBoxEdit->InitModel(modelPath, bBoxEdit->mRoot);
// **************** part0: inside code segment of func call **********************/
            osg::ref_ptr<osgViewer::Viewer> mViewer = bBoxEdit->pWidget->getOsgViewer();
            // Add a Stats Handler to the viewer
            mViewer->addEventHandler(new osgViewer::StatsHandler);
            // Add the Camera to the Viewer
            osg::ref_ptr<osg::Camera> camera = mViewer->getCamera();
            // Set projection matrix and camera attribtues
            camera->setClearMask(GL_DEPTH_BUFFER_BIT | GL_COLOR_BUFFER_BIT);
            camera->setClearColor(osg::Vec3f(0.2f, 0.2f, 0.4f, 1.0f));
            //mViewer->addSlave(camera.get());
            mViewer->setCamera(camera.get());
            // Set the Scene Data
// *************************** part1: func call **********************************/
            // bBoxEdit->InitCameraConfig();
```
如上代码段，是一段qt程序中，在MainWindow的一个子函数的一段代码，其中bBoxEdit是一个自定义的供调用的类，
问题来了， part0的代码就是把part2的代码拿出来，仅仅使用part1的代码就会出错，仅仅使用part2就不会，请推测原因？
这里给出part1的实现代码：
```cpp
void QOsgWidget::InitCameraConfig() {
    // Create the viewer for this window
    mViewer = this->pWidget->getOsgViewer();
    // Add a Stats Handler to the viewer
    mViewer->addEventHandler(new osgViewer::StatsHandler);
    // Add the Camera to the Viewer
    osg::ref_ptr<osg::Camera> camera = mViewer->getCamera();
    // Set projection matrix and camera attribtues
    camera->setClearMask(GL_DEPTH_BUFFER_BIT | GL_COLOR_BUFFER_BIT);
    camera->setClearColor(osg::Vec3f(0.2f, 0.2f, 0.4f, 1.0f));
    //mViewer->addSlave(camera.get());
    mViewer->setCamera(camera.get());
    // Add the Camera Manipulator to the Viewer
    osg::ref_ptr<osgGA::TrackballManipulator> trackball = new osgGA::TrackballManipulator();
    mViewer->setCameraManipulator(trackball.get());
    // Set the Scene Data
    mViewer->setSceneData(mRoot.get());
}
```
#### 2.2 错误原因推测：
首先想到，这肯定是指针带来的问题，指针和作用域和代码范围息息相关，所以放到函数里面和放到mainwindow的一个子函数的随便的一处，最大的区别在于，
- 0 part2的情况：part2里面的函数调用所用到的指针，是存在qosgwidget的类的栈空间的，意味着只要类不析构，那么该指针所指向的内存就不会被回收。
- 1 part1的情况：part1里面申请的内存是在mainwindow的一个子函数调用里面申请的，意味着该指针，在该子函数调用结束，它指向的内存会被回收，倘若这一块内存里运行的函数是我们恰恰不希望他在函数结束后就消失，那么我们就需要把这个指针存在一个 __‘安全’__ 的地方。所以你需要存在哪里？  因为上面可以知道，该指针的内存里的函数是被 qosgwidget这个类所需要的,也就是当这个类结束啦，这个指针才会被回收，所以我们把指针存在这里，就不会出现上面的问题了。
#### 2.3 得出结论（个人观点）
cpp的内存管理问题：
- 0 尽量不要在业务流程里申请内存，释放内存，如果遇到需要申请内存和释放的地方，请把这一块儿写成一个类，
用类的变量来保存内存指针，用类的析构来释放内存。
- 1 **重复1的观点：基于类作为内存管理的最小粒度，不要基于指针**
## 2021/06/15
### 1 colmap online拼接cmvs
colmap-dev的编译命令
```py
python scripts/python/build.py \
    --build_path "F:/prjs/onlineColmap/colmap-dev/build" \
    --colmap_path "F:/prjs/onlineColmap/colmap-dev" \
    --boost_path "F:/BASE_ENV/forOpenMVS/boost_1_73_0_v140" \
    --qt_path "F:/BASE_ENV/forOpenMVS/qt_msvc2015_64/msvc2015_64" \
    --cgal_path "F:/BASE_ENV/forOpenMVS/CGAL-5.1/build" \
    --cmake_generator "Visual Studio 14" \
    --with_cuda \
    --cuda_path "C:/Program Files/NVIDIA GPU Computing Toolkit/CUDA/v10.2" \
python scripts/python/build.py \
    --build_path "F:/prjs/onlineColmap/modifyCmake/colmap-dev/build" \
    --colmap_path "F:/prjs/onlineColmap/modifyCmake/colmap-dev" \
    --boost_path "F:/BASE_ENV/forOpenMVS/boost_1_73_0_v140" \
    --qt_path "F:/BASE_ENV/forOpenMVS/qt_msvc2015_64/msvc2015_64" \
    --cgal_path "F:/BASE_ENV/forOpenMVS/CGAL-5.1/build" \
    --cmake_generator "Visual Studio 14" \
    --with_cuda \
    --cuda_path "C:/Program Files/NVIDIA GPU Computing Toolkit/CUDA/v10.2" \
```
由于pointCloud库的依赖，我们需要添加如下：
```sh
# include
F:/prjs/onlineColmap/OrbSlam24Windows/OrbSlam24Windows/Thirdparty/pmvsOnline/../opencv3.1.0/build/include;
F:/prjs/onlineColmap/OrbSlam24Windows/OrbSlam24Windows/Thirdparty/pmvsOnline/../opencv3.1.0/build/include/opencv;
F:/prjs/onlineColmap/OrbSlam24Windows/OrbSlam24Windows/Thirdparty/pmvsOnline/../opencv3.1.0/build/include/opencv2;
F:/prjs/onlineColmap/OrbSlam24Windows/OrbSlam24Windows/Thirdparty/pmvsOnline/include;
F:/prjs/onlineColmap/OrbSlam24Windows/OrbSlam24Windows/Thirdparty/pmvsOnline/thirdParty;
F:/prjs/onlineColmap/OrbSlam24Windows/OrbSlam24Windows/Thirdparty/pmvsOnline/thirdParty/graclus1.2/metisLib;
F:/prjs/onlineColmap/OrbSlam24Windows/OrbSlam24Windows/Thirdparty/pmvsOnline/thirdParty/nlopt-2.4.2/api;
F:/prjs/onlineColmap/OrbSlam24Windows/OrbSlam24Windows/Thirdparty/pmvsOnline/thirdParty/cimg;
F:/prjs/onlineColmap/OrbSlam24Windows/OrbSlam24Windows/Thirdparty/pmvsOnline/thirdParty/tinycthread;
F:/prjs/onlineColmap/OrbSlam24Windows/OrbSlam24Windows/Thirdparty/pmvsOnline/../eigen3.2.9;
F:/prjs/onlineColmap/OrbSlam24Windows/OrbSlam24Windows/Thirdparty/pmvsOnline/thirdParty/miniBoost;
F:/prjs/onlineColmap/OrbSlam24Windows/OrbSlam24Windows/Thirdparty/pmvsOnline/thirdParty/jpeg;
F:/prjs/onlineColmap/OrbSlam24Windows/OrbSlam24Windows/Thirdparty/pmvsOnline/build/thirdParty/jpeg;
F:/prjs/onlineColmap/OrbSlam24Windows/OrbSlam24Windows/Thirdparty/Pangolin/include;
F:/prjs/onlineColmap/OrbSlam24Windows/OrbSlam24Windows/Thirdparty/Pangolin/include/pangolin;
F:/prjs/onlineColmap/OrbSlam24Windows/OrbSlam24Windows/Thirdparty/Pangolin/include;
F:/prjs/ThirdParty/glew-2.0.0/include;
%(AdditionalIncludeDirectories)
# lib
F:/prjs/onlineColmap/modifyCMake/colmap-dev/build/__install__/lib/image_lib.lib
F:/prjs/onlineColmap/modifyCMake/colmap-dev/build/__install__/lib/jpeg.lib
F:/prjs/onlineColmap/modifyCMake/colmap-dev/build/__install__/lib/nlopt.lib
F:/prjs/onlineColmap/modifyCMake/colmap-dev/build/__install__/lib/numeric_lib.lib
F:/prjs/onlineColmap/modifyCMake/colmap-dev/build/__install__/lib/pmvs_lib.lib
F:/prjs/onlineColmap/modifyCMake/colmap-dev/build/__install__/lib/PointCloud.lib
F:/prjs/onlineColmap/modifyCMake/colmap-dev/build/__install__/lib/tinycthread.lib
F:/prjs/onlineColmap/modifyCMake/colmap-dev/build/__install__/lib/opencv_world310.lib
F:/prjs/ThirdParty/glew-2.0.0/lib/Release/x64/glew32s.lib
F:/prjs/ThirdParty/glew-2.0.0/lib/Release/x64/glew32.lib
opengl32.lib
F:/prjs/ORB_SLAM3_Fix/ORB_SLAM3/Thirdparty/Pangolin/lib/Release/pangolin.lib
F:/BASE_ENV/forOpenMVS/libpng/lib/libpng16_static.lib
F:/BASE_ENV/forOpenMVS/zlib/lib/zlibstatic.lib
## attention: the last 3 can be retried from pangolin on github
F:/prjs/onlineColmap/modifyCMake/colmap-dev/build/__install__/lib/libspqr.lib
F:/prjs/onlineColmap/modifyCMake/colmap-dev/build/__install__/lib/libcholmod.lib
F:/prjs/onlineColmap/modifyCMake/colmap-dev/build/__install__/lib/libccolamd.lib
F:/prjs/onlineColmap/modifyCMake/colmap-dev/build/__install__/lib/libcamd.lib
F:/prjs/onlineColmap/modifyCMake/colmap-dev/build/__install__/lib/libcolamd.lib
F:/prjs/onlineColmap/modifyCMake/colmap-dev/build/__install__/lib/libamd.lib
F:/prjs/onlineColmap/modifyCMake/colmap-dev/build/__install__/lib64/lapack_blas_windows/liblapack.lib
F:/prjs/onlineColmap/modifyCMake/colmap-dev/build/__install__/lib64/lapack_blas_windows/libblas.lib
F:/prjs/onlineColmap/modifyCMake/colmap-dev/build/__install__/lib/suitesparseconfig.lib
F:/prjs/onlineColmap/modifyCMake/colmap-dev/build/__install__/lib/metis.lib
F:/prjs/onlineColmap/modifyCMake/colmap-dev/build/__install__/lib/libcxsparse.lib
```
```
colmap's lib:
# lib
F:/prjs/onlineColmap/modifyCMake/colmap-dev/build/__install__/lib/image_lib.lib
F:/prjs/onlineColmap/modifyCMake/colmap-dev/build/__install__/lib/jpeg.lib
F:/prjs/onlineColmap/modifyCMake/colmap-dev/build/__install__/lib/nlopt.lib
F:/prjs/onlineColmap/modifyCMake/colmap-dev/build/__install__/lib/numeric_lib.lib
F:/prjs/onlineColmap/modifyCMake/colmap-dev/build/__install__/lib/pmvs_lib.lib
F:/prjs/onlineColmap/modifyCMake/colmap-dev/build/__install__/lib/PointCloud.lib
F:/prjs/onlineColmap/modifyCMake/colmap-dev/build/__install__/lib/tinycthread.lib
F:/prjs/onlineColmap/modifyCMake/colmap-dev/build/__install__/lib/opencv_world310.lib
F:\BASE_ENV\forOpenMVS\boost_1_73_0_v140\lib64-msvc-14.0\libboost_filesystem-vc140-mt-x64-1_73.lib
F:\BASE_ENV\forOpenMVS\boost_1_73_0_v140\lib64-msvc-14.0\libboost_program_options-vc140-mt-x64-1_73.lib
F:\BASE_ENV\forOpenMVS\boost_1_73_0_v140\lib64-msvc-14.0\libboost_regex-vc140-mt-x64-1_73.lib
F:\BASE_ENV\forOpenMVS\boost_1_73_0_v140\lib64-msvc-14.0\libboost_system-vc140-mt-x64-1_73.lib
```
pmvs的主要输入文件以及参考文档：
[https://www.di.ens.fr/pmvs/documentation.html](https://www.di.ens.fr/pmvs/documentation.html)
测试命令如下：
```sh
./colmap.exe denseol \
  --sparse_path F:/prjs/onlineColmap/germany/res/sparse \
  --dense_path F:/prjs/onlineColmap/germany/res/dense \
  --image_path F:/prjs/onlineColmap/germany/images \
  --vocab_tree_path F:/prjs/onlineColmap/modifyCMake/colmap-dev/vocab_tree_flickr100K_words32K.bin
./colmap.exe funcsparseol \
  --sparse_path F:/prjs/onlineColmap/germany/res/sparse \
  --image_path F:/prjs/onlineColmap/germany/images \
  --vocab_tree_path F:/prjs/onlineColmap/modifyCMake/colmap-dev/vocab_tree_flickr100K_words32K.bin
```
--sparse_path F:/prjs/onlineColmap/ShiYan/res/sparse   --dense_path F:/prjs/onlineColmap/ShiYan/res/dense  --image_path F:/prjs/onlineColmap/ShiYan/images --vocab_tree_path F:/prjs/onlineColmap/modifyCMake/colmap-dev/vocab_tree_flickr100K_words32K.bin
denseol  --sparse_path F:/prjs/onlineColmap/germany/res/sparse --dense_path F:/prjs/onlineColmap/germany/res/dense  --image_path F:/prjs/onlineColmap/germany/images --vocab_tree_path F:/prjs/onlineColmap/modifyCMake/colmap-dev/vocab_tree_flickr100K_words32K.bin
```sh
# test germany sh 
rm -rf /f/prjs/onlineColmap/germany/res/sparse/*
cp -f ../../colmap/__build__/src/exe/Release/* .
./colmap.exe denseol \
  --sparse_path F:/prjs/onlineColmap/germany/res/sparse \
  --dense_path F:/prjs/onlineColmap/germany/res/dense \
  --image_path F:/prjs/onlineColmap/germany/images \
  --vocab_tree_path F:/prjs/onlineColmap/modifyCMake/colmap-dev/vocab_tree_flickr100K_words32K.bin
```
## 2021/07/14
### 1 
```sh
F:\prjs\ORB_SLAM3_Fix\ORB_SLAM3;F:\prjs\ORB_SLAM3_Fix\ORB_SLAM3\include;F:\prjs\ORB_SLAM3_Fix\ORB_SLAM3\include\CameraModels;F:\BASE_ENV\forOpenMVS\eigen;F:\BASE_ENV\strawberry\c\include;F:\BASE_ENV\forOpenMVS\boost_1_73_0_v140;F:\prjs\ORB_SLAM3_Fix\ORB_SLAM3\Thirdparty\Pangolin\include;F:\prjs\ORB_SLAM3_Fix\ORB_SLAM3\Thirdparty\Pangolin\build\src\include;F:\prjs\ORB_SLAM3_Fix\ORB_SLAM3\Thirdparty\Pangolin\install\include;F:\BASE_ENV\forOpenMVS\opencv\build;F:\BASE_ENV\forOpenMVS\opencv\include;F:\BASE_ENV\forOpenMVS\opencv\modules\core\include;F:\BASE_ENV\forOpenMVS\opencv\modules\flann\include;F:\BASE_ENV\forOpenMVS\opencv\modules\imgproc\include;F:\BASE_ENV\forOpenMVS\opencv\modules\ml\include;F:\BASE_ENV\forOpenMVS\opencv\modules\photo\include;F:\BASE_ENV\forOpenMVS\opencv\modules\dnn\include;F:\BASE_ENV\forOpenMVS\opencv\modules\features2d\include;F:\BASE_ENV\forOpenMVS\opencv\modules\imgcodecs\include;F:\BASE_ENV\forOpenMVS\opencv\modules\videoio\include;F:\BASE_ENV\forOpenMVS\opencv\modules\calib3d\include;F:\BASE_ENV\forOpenMVS\opencv\modules\highgui\include;F:\BASE_ENV\forOpenMVS\opencv\modules\objdetect\include;F:\BASE_ENV\forOpenMVS\opencv\modules\stitching\include;F:\BASE_ENV\forOpenMVS\opencv\modules\ts\include;F:\BASE_ENV\forOpenMVS\opencv\modules\video\include;F:\BASE_ENV\forOpenMVS\opencv\modules\gapi\include;%(AdditionalIncludeDirectories)
```
## 2021/07/18
## glog使用：
项目地址：
[git@github.com:xychen5/tryGlog.git](git@github.com:xychen5/tryGlog.git)
推荐使用类似于clion的ide，然后打开该项目，即可编译运行。
### 1 主要作用：
**能够将glog的日志在cmd中打印**
主要调用了函数：
```cpp
   google::SetStderrLogging(google::INFO); // print the logs whose severity > [info]
```
### 2 output：
样例输出代码如下：
```log
I0718 16:09:07.626883 18628 main.cpp:13] glog used in cmd!!
W0718 16:09:07.627887 18628 main.cpp:14] glog used in cmd!!
E0718 16:09:07.628882 18628 main.cpp:15] glog used in cmd!!
F0718 16:09:07.628882 18628 main.cpp:16] glog used in cmd!!
```
## 2021/07/19
### 1 ffmpeg 解帧
```sh
ffmpeg -i DJI_20210615164633_0003_W.MP4 -r 3 images/%4d.jpg
```
### 2 reinterpret_cast<> 理解以及典型应用：
对于其他的例如static_cast<>等的应用，参考：[http://www.cplusplus.com/doc/tutorial/typecasting/](http://www.cplusplus.com/doc/tutorial/typecasting/)<br>
以下引用自: [https://stackoverflow.com/questions/573294/when-to-use-reinterpret-cast](https://stackoverflow.com/questions/573294/when-to-use-reinterpret-cast)<br>
Here is a variant of Avi Ginsburg's program which clearly illustrates the property of reinterpret_cast mentioned by Chris Luengo, flodin, and cmdLP: that the compiler treats the pointed-to memory location as if it were an object of the new type:
```cpp
#include <iostream>
#include <string>
#include <iomanip>
using namespace std;
class A
{
public:
    int i;
};
class B : public A
{
public:
    virtual void f() {}
};
int main()
{
    string s;
    B b;
    b.i = 0;
    A* as = static_cast<A*>(&b);
    A* ar = reinterpret_cast<A*>(&b);
    B* c = reinterpret_cast<B*>(ar);
    
    cout << "as->i = " << hex << setfill('0')  << as->i << "\n";
    cout << "ar->i = " << ar->i << "\n";
    cout << "b.i   = " << b.i << "\n";
    cout << "c->i  = " << c->i << "\n";
    cout << "\n";
    cout << "&(as->i) = " << &(as->i) << "\n";
    cout << "&(ar->i) = " << &(ar->i) << "\n";
    cout << "&(b.i) = " << &(b.i) << "\n";
    cout << "&(c->i) = " << &(c->i) << "\n";
    cout << "\n";
    cout << "&b = " << &b << "\n";
    cout << "as = " << as << "\n";
    cout << "ar = " << ar << "\n";
    cout << "c  = " << c  << "\n";
    
    cout << "Press ENTER to exit.\n";
    getline(cin,s);
}
```
Which results in output like this:
```out
as->i = 0
ar->i = 50ee64
b.i   = 0
c->i  = 0
&(as->i) = 00EFF978
&(ar->i) = 00EFF974
&(b.i)   = 00EFF978
&(c->i)  = 00EFF978
&b = 00EFF974
as = 00EFF978
ar = 00EFF974
c  = 00EFF974
Press ENTER to exit.
```
It can be seen that the B object is built in memory as B-specific data first, followed by the embedded A object. The static_cast correctly returns the address of the embedded A object, and the pointer created by static_cast correctly gives the value of the data field. The pointer generated by reinterpret_cast treats b's memory location as if it were a plain A object, and so when the pointer tries to get the data field it returns some B-specific data as if it were the contents of this field.
应用如下：
下面的应用根据输入的类型T判断后使用了reinterpret_cast去转换；
```cpp
template <typename T>
void OptionManager::RegisterOption(const std::string& name, const T* option) {
  if (std::is_same<T, bool>::value) {
    options_bool_.emplace_back(name, reinterpret_cast<const bool*>(option));
  } else if (std::is_same<T, int>::value) {
    options_int_.emplace_back(name, reinterpret_cast<const int*>(option));
  } else if (std::is_same<T, double>::value) {
    options_double_.emplace_back(name, reinterpret_cast<const double*>(option));
  } else if (std::is_same<T, std::string>::value) {
    options_string_.emplace_back(name,
                                 reinterpret_cast<const std::string*>(option));
  } else {
    LOG(FATAL) << "Unsupported option type";
  }
}
```
## 2021/07/20 
### 1 进程句柄数不断攀升导致被kill
是不是打开的某些文件没有被close
## 2021/08/04
### 1 std::thread传入引用值需要使用std::ref
```cpp
void main() {
    while(1){
        ...<省略>...
        if (!initializedFlag) {
            initializedFlag = true;
            // viewThd = new std::thread(viewThread, camVecToDraw); // wrong way
            viewThd = new std::thread(viewThread, std::ref(camVecToDraw)); // right way
        }
        ...<省略>...
        addCamToDrawVec(imgData.image, camVecToDraw);
        camVecToDraw;
    }
    
    viewThd.join();
    delete viewThd;
    viewThd = nullptr;
}
void viewThread(std::vector<pangolin::OpenGlMatrix>& camVecToDraw) {
    while(!shallQuit()) {
        // render some cameras according to camVecToDraw
        ...<省略>...
    }
}
```
## 2021/08/24
### 1 pmvs论文阅读 
- 1 文章 Accurate, Dense, and Robust Multiview Stereopsis
- 提出 patch-based MVS algorithm
 
- 2 关键词理解：
  - 2.1 patch: 估计模型表面的一个tagent平面，更具体的： 3维的一个矩形，其中一边平行于相机拍的图片，范围是5*5或者7*7的一个矩形
  - 2.2 Photometric Discrepancy Function 光学差异函数： 用来恢复光学差异小的那些patches
## 2021/08/25
### 1 mysql数据库表设计
```sql
/*
SQLyog 企业版 - MySQL GUI v8.14 
MySQL - 5.5.40 : Database - HdMarket
*********************************************************************
*/
/*!40101 SET NAMES utf8 */;
/*!40101 SET SQL_MODE=''*/;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;
CREATE DATABASE /*!32312 IF NOT EXISTS*/`FireTest` /*!40100 DEFAULT CHARACTER SET utf8 COLLATE utf8_unicode_ci */;
USE `FireTest`;
/*Table structure for table `address` */
DROP TABLE IF EXISTS `message`;
CREATE TABLE `mesage` (
  `id` varchar(200) NOT NULL AUTO_INCREMENT COMMENT '主键ID',
  `contact` varchar(15) COLLATE utf8_unicode_ci DEFAULT NULL COMMENT '联系人姓名',
  `addressDesc` varchar(50) COLLATE utf8_unicode_ci DEFAULT NULL COMMENT '收货地址明细',
  `postCode` varchar(15) COLLATE utf8_unicode_ci DEFAULT NULL COMMENT '邮编',
  `tel` varchar(20) COLLATE utf8_unicode_ci DEFAULT NULL COMMENT '联系人电话',
  `createdBy` bigint(20) DEFAULT NULL COMMENT '创建者',
  `creationDate` datetime DEFAULT NULL COMMENT '创建时间',
  `modifyBy` bigint(20) DEFAULT NULL COMMENT '修改者',
  `modifyDate` datetime DEFAULT NULL COMMENT '修改时间',
  `userId` bigint(20) DEFAULT NULL COMMENT '用户ID',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=7 DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*Data for the table `address` */
insert  into `address`(`id`,`contact`,`addressDesc`,`postCode`,`tel`,`createdBy`,`creationDate`,`modifyBy`,`modifyDate`,`userId`) values (1,'王丽','杭州市上城区潮鸣寺巷44号','100010','13678789999',1,'2016-04-13 00:00:00',NULL,NULL,1),(2,'张红丽','杭州市西湖区文新街3号','100000','18567672312',1,'2016-04-13 00:00:00',NULL,NULL,1),(3,'任志强','杭州市上城区美术馆后街23号','100021','13387906742',1,'2016-04-13 00:00:00',NULL,NULL,1),(4,'曹颖','杭州市滨江区滨江门南大街14号','100053','13568902323',1,'2016-04-13 00:00:00',NULL,NULL,2),(5,'李慧','杭州市西湖区三墩路南三巷3号','100032','18032356666',1,'2016-04-13 00:00:00',NULL,NULL,3),(6,'王国强','杭州市江干区下沙工业区18号','100061','13787882222',1,'2016-04-13 00:00:00',NULL,NULL,3);
/*Table structure for table `bill` */
DROP TABLE IF EXISTS `bill`;
CREATE TABLE `bill` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT COMMENT '主键ID',
  `billCode` varchar(20) COLLATE utf8_unicode_ci DEFAULT NULL COMMENT '账单编码',
  `productName` varchar(20) COLLATE utf8_unicode_ci DEFAULT NULL COMMENT '商品名称',
  `productDesc` varchar(50) COLLATE utf8_unicode_ci DEFAULT NULL COMMENT '商品描述',
  `productUnit` varchar(10) COLLATE utf8_unicode_ci DEFAULT NULL COMMENT '商品单位',
  `productCount` decimal(20,2) DEFAULT NULL COMMENT '商品数量',
  `totalPrice` decimal(20,2) DEFAULT NULL COMMENT '商品总额',
  `isPayment` int(10) DEFAULT NULL COMMENT '是否支付（1：未支付 2：已支付）',
  `createdBy` bigint(20) DEFAULT NULL COMMENT '创建者（userId）',
  `creationDate` datetime DEFAULT NULL COMMENT '创建时间',
  `modifyBy` bigint(20) DEFAULT NULL COMMENT '更新者（userId）',
  `modifyDate` datetime DEFAULT NULL COMMENT '更新时间',
  `providerId` bigint(20) DEFAULT NULL COMMENT '供应商ID',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=19 DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*Data for the table `bill` */
insert  into `bill`(`id`,`billCode`,`productName`,`productDesc`,`productUnit`,`productCount`,`totalPrice`,`isPayment`,`createdBy`,`creationDate`,`modifyBy`,`modifyDate`,`providerId`) values (1,'BILL2016_001','洗发水、护发素','日用品-洗发、护发','瓶','500.00','25000.00',2,1,'2014-12-14 13:02:03',NULL,NULL,13),(2,'BILL2016_002','香皂、肥皂、药皂','日用品-皂类','块','1000.00','10000.00',2,1,'2016-03-23 04:20:40',NULL,NULL,13),(3,'BILL2016_003','大豆油','食品-食用油','斤','300.00','5890.00',2,1,'2014-12-14 13:02:03',NULL,NULL,6),(4,'BILL2016_004','橄榄油','食品-进口食用油','斤','200.00','9800.00',2,1,'2013-10-10 03:12:13',NULL,NULL,7),(5,'BILL2016_005','洗洁精','日用品-厨房清洁','瓶','500.00','7000.00',2,1,'2014-12-14 13:02:03',NULL,NULL,9),(6,'BILL2016_006','美国大杏仁','食品-坚果','袋','300.00','5000.00',2,1,'2016-04-14 06:08:09',NULL,NULL,4),(7,'BILL2016_007','沐浴液、精油','日用品-沐浴类','瓶','500.00','23000.00',1,1,'2016-07-22 10:10:22',NULL,NULL,14),(8,'BILL2016_008','不锈钢盘碗','日用品-厨房用具','个','600.00','6000.00',2,1,'2016-04-14 05:12:13',NULL,NULL,14),(9,'BILL2016_009','塑料杯','日用品-杯子','个','350.00','1750.00',2,1,'2016-02-04 11:40:20',NULL,NULL,14),(10,'BILL2016_010','豆瓣酱','食品-调料','瓶','200.00','2000.00',2,1,'2013-10-29 05:07:03',NULL,NULL,8),(11,'BILL2016_011','海之蓝','饮料-国酒','瓶','50.00','10000.00',1,1,'2016-04-14 16:16:00',NULL,NULL,1),(12,'BILL2016_012','芝华士','饮料-洋酒','瓶','20.00','6000.00',1,1,'2016-09-09 17:00:00',NULL,NULL,1),(13,'BILL2016_013','长城红葡萄酒','饮料-红酒','瓶','60.00','800.00',2,1,'2016-11-14 15:23:00',NULL,NULL,1),(14,'BILL2016_014','泰国香米','食品-大米','斤','400.00','5000.00',2,1,'2016-10-09 15:20:00',NULL,NULL,3),(15,'BILL2016_015','东北大米','食品-大米','斤','600.00','4000.00',2,1,'2016-11-14 14:00:00',NULL,NULL,3),(16,'BILL2016_016','可口可乐','饮料','瓶','2000.00','6000.00',2,1,'2012-03-27 13:03:01',NULL,NULL,2),(17,'BILL2016_017','脉动','饮料','瓶','1500.00','4500.00',2,1,'2016-05-10 12:00:00',NULL,NULL,2),(18,'BILL2016_018','哇哈哈','饮料','瓶','2000.00','4000.00',2,1,'2015-11-24 15:12:03',NULL,NULL,2);
/*Table structure for table `provider` */
DROP TABLE IF EXISTS `provider`;
CREATE TABLE `provider` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT COMMENT '主键ID',
  `proCode` varchar(20) COLLATE utf8_unicode_ci DEFAULT NULL COMMENT '供应商编码',
  `proName` varchar(20) COLLATE utf8_unicode_ci DEFAULT NULL COMMENT '供应商名称',
  `proDesc` varchar(50) COLLATE utf8_unicode_ci DEFAULT NULL COMMENT '供应商详细描述',
  `proContact` varchar(20) COLLATE utf8_unicode_ci DEFAULT NULL COMMENT '供应商联系人',
  `proPhone` varchar(20) COLLATE utf8_unicode_ci DEFAULT NULL COMMENT '联系电话',
  `proAddress` varchar(50) COLLATE utf8_unicode_ci DEFAULT NULL COMMENT '地址',
  `proFax` varchar(20) COLLATE utf8_unicode_ci DEFAULT NULL COMMENT '传真',
  `createdBy` bigint(20) DEFAULT NULL COMMENT '创建者（userId）',
  `creationDate` datetime DEFAULT NULL COMMENT '创建时间',
  `modifyDate` datetime DEFAULT NULL COMMENT '更新时间',
  `modifyBy` bigint(20) DEFAULT NULL COMMENT '更新者（userId）',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=16 DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*Data for the table `provider` */
insert  into `provider`(`id`,`proCode`,`proName`,`proDesc`,`proContact`,`proPhone`,`proAddress`,`proFax`,`createdBy`,`creationDate`,`modifyDate`,`modifyBy`) values (1,'BJ_GYS001','杭州三木堂商贸有限公司','长期合作伙伴，主营产品:茅台、五粮液、郎酒、酒鬼酒、泸州老窖、赖茅酒、法国红酒等','张国强','13566667777','杭州市丰台区育芳园北路','010-58858787',1,'2013-03-21 16:52:07',NULL,NULL),(2,'HB_GYS001','石家庄帅益食品贸易有限公司','长期合作伙伴，主营产品:饮料、水饮料、植物蛋白饮料、休闲食品、果汁饮料、功能饮料等','王军','13309094212','河北省石家庄新华区','0311-67738876',1,'2016-04-13 04:20:40',NULL,NULL),(3,'GZ_GYS001','深圳市泰香米业有限公司','初次合作伙伴，主营产品：良记金轮米,龙轮香米等','郑程瀚','13402013312','广东省深圳市福田区深南大道6006华丰大厦','0755-67776212',1,'2014-03-21 16:56:07',NULL,NULL),(4,'GZ_GYS002','深圳市喜来客商贸有限公司','长期合作伙伴，主营产品：坚果炒货.果脯蜜饯.天然花茶.营养豆豆.特色美食.进口食品.海味零食.肉脯肉','林妮','18599897645','广东省深圳市福龙工业区B2栋3楼西','0755-67772341',1,'2013-03-22 16:52:07',NULL,NULL),(5,'JS_GYS001','兴化佳美调味品厂','长期合作伙伴，主营产品：天然香辛料、鸡精、复合调味料','徐国洋','13754444221','江苏省兴化市林湖工业区','0523-21299098',1,'2015-11-22 16:52:07',NULL,NULL),(6,'BJ_GYS002','杭州纳福尔食用油有限公司','长期合作伙伴，主营产品：山茶油、大豆油、花生油、橄榄油等','马莺','13422235678','杭州市滨江区珠江帝景1号楼','010-588634233',1,'2012-03-21 17:52:07',NULL,NULL),(7,'BJ_GYS003','杭州国粮食用油有限公司','初次合作伙伴，主营产品：花生油、大豆油、小磨油等','王驰','13344441135','杭州大兴青云店开发区','010-588134111',1,'2016-04-13 00:00:00',NULL,NULL),(8,'ZJ_GYS001','慈溪市广和绿色食品厂','长期合作伙伴，主营产品：豆瓣酱、黄豆酱、甜面酱，辣椒，大蒜等农产品','薛圣丹','18099953223','浙江省宁波市慈溪周巷小安村','0574-34449090',1,'2013-11-21 06:02:07',NULL,NULL),(9,'GX_GYS001','优百商贸有限公司','长期合作伙伴，主营产品：日化产品','李立国','13323566543','广西南宁市秀厢大道42-1号','0771-98861134',1,'2013-03-21 19:52:07',NULL,NULL),(10,'JS_GYS002','南京火头军信息技术有限公司','长期合作伙伴，主营产品：不锈钢厨具等','陈女士','13098992113','江苏省南京市浦口区浦口大道1号新城总部大厦A座903室','025-86223345',1,'2013-03-25 16:52:07',NULL,NULL),(11,'GZ_GYS003','广州市白云区美星五金制品厂','长期合作伙伴，主营产品：海绵床垫、坐垫、靠垫、海绵枕头、头枕等','梁天','13562276775','广州市白云区钟落潭镇福龙路20号','020-85542231',1,'2016-12-21 06:12:17',NULL,NULL),(12,'BJ_GYS004','杭州隆盛日化科技','长期合作伙伴，主营产品：日化环保清洗剂，家居洗涤专卖、洗涤用品网、墙体除霉剂、墙面霉菌清除剂等','孙欣','13689865678','杭州市大兴区旧宫','010-35576786',1,'2014-11-21 12:51:11',NULL,NULL),(13,'SD_GYS001','山东豪克华光联合发展有限公司','长期合作伙伴，主营产品：洗衣皂、洗衣粉、洗衣液、洗洁精、消杀类、香皂等','吴洪转','13245468787','山东济阳济北工业区仁和街21号','0531-53362445',1,'2015-01-28 10:52:07',NULL,NULL),(14,'JS_GYS003','无锡喜源坤商行','长期合作伙伴，主营产品：日化品批销','周一清','18567674532','江苏无锡盛岸西路','0510-32274422',1,'2016-04-23 11:11:11',NULL,NULL),(15,'ZJ_GYS002','乐摆日用品厂','长期合作伙伴，主营产品：各种中、高档塑料杯，塑料乐扣水杯（密封杯）、保鲜杯（保鲜盒）、广告杯、礼品杯','王世杰','13212331567','浙江省金华市义乌市义东路','0579-34452321',1,'2016-08-22 10:01:30',NULL,NULL);
/*Table structure for table `role` */
DROP TABLE IF EXISTS `role`;
CREATE TABLE `role` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT COMMENT '主键ID',
  `roleCode` varchar(15) COLLATE utf8_unicode_ci DEFAULT NULL COMMENT '角色编码',
  `roleName` varchar(15) COLLATE utf8_unicode_ci DEFAULT NULL COMMENT '角色名称',
  `createdBy` bigint(20) DEFAULT NULL COMMENT '创建者',
  `creationDate` datetime DEFAULT NULL COMMENT '创建时间',
  `modifyBy` bigint(20) DEFAULT NULL COMMENT '修改者',
  `modifyDate` datetime DEFAULT NULL COMMENT '修改时间',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*Data for the table `role` */
insert  into `role`(`id`,`roleCode`,`roleName`,`createdBy`,`creationDate`,`modifyBy`,`modifyDate`) values (1,'ADMIN','系统管理员',1,'2016-04-13 00:00:00',NULL,NULL),(2,'MANAGER','经理',1,'2016-04-13 00:00:00',NULL,NULL),(3,'EMPLOYEE','普通员工',1,'2016-04-13 00:00:00',NULL,NULL);
/*Table structure for table `user` */
DROP TABLE IF EXISTS `user`;
CREATE TABLE `user` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT COMMENT '主键ID',
  `userCode` varchar(15) COLLATE utf8_unicode_ci DEFAULT NULL COMMENT '用户编码',
  `userName` varchar(15) COLLATE utf8_unicode_ci DEFAULT NULL COMMENT '用户名称',
  `userPassword` varchar(15) COLLATE utf8_unicode_ci DEFAULT NULL COMMENT '用户密码',
  `gender` int(10) DEFAULT NULL COMMENT '性别（1:女、 2:男）',
  `birthday` date DEFAULT NULL COMMENT '出生日期',
  `phone` varchar(15) COLLATE utf8_unicode_ci DEFAULT NULL COMMENT '手机',
  `address` varchar(30) COLLATE utf8_unicode_ci DEFAULT NULL COMMENT '地址',
  `userRole` bigint(20) DEFAULT NULL COMMENT '用户角色（取自角色表-角色id）',
  `createdBy` bigint(20) DEFAULT NULL COMMENT '创建者（userId）',
  `creationDate` datetime DEFAULT NULL COMMENT '创建时间',
  `modifyBy` bigint(20) DEFAULT NULL COMMENT '更新者（userId）',
  `modifyDate` datetime DEFAULT NULL COMMENT '更新时间',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=16 DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;
/*Data for the table `user` */
insert  into `user`(`id`,`userCode`,`userName`,`userPassword`,`gender`,`birthday`,`phone`,`address`,`userRole`,`createdBy`,`creationDate`,`modifyBy`,`modifyDate`) values (1,'admin','系统管理员','1234567',1,'1983-10-10','13688889999','杭州市西湖区文二路207号',1,1,'2013-03-21 16:52:07',NULL,NULL),(2,'liming','李明','0000000',2,'1983-12-10','13688884457','杭州市上城区凤起路9号',2,1,'2014-12-31 19:52:09',NULL,NULL),(5,'hanlubiao','韩路彪','0000000',2,'1984-06-05','18567542321','杭州市滨江区会展中心12号',2,1,'2014-12-31 19:52:09',NULL,NULL),(6,'zhanghua','张华','0000000',1,'1983-06-15','13544561111','杭州市西湖区学院路61号',3,1,'2013-02-11 10:51:17',NULL,NULL),(7,'wangyang','王洋','0000000',2,'1982-12-31','13444561124','杭州市西湖区文欣商务楼',3,1,'2014-06-11 19:09:07',NULL,NULL),(8,'zhaoyan','赵燕','0000000',1,'1986-03-07','18098764545','杭州市西湖区文欣苑小区10号楼',3,1,'2016-04-21 13:54:07',NULL,NULL),(10,'sunlei','孙磊','0000000',2,'1981-01-04','13387676765','杭州市滨江区管庄新月小区12楼',3,1,'2015-05-06 10:52:07',NULL,NULL),(11,'sunxing','孙兴','0000000',2,'1978-03-12','13367890900','杭州市滨江区城南大街10号',3,1,'2016-11-09 16:51:17',NULL,NULL),(12,'zhangchen','张晨','0000000',1,'1986-03-28','18098765434','滨江区北柏林爱乐三期13号楼',3,1,'2016-08-09 05:52:37',1,'2016-04-14 14:15:36'),(13,'dengchao','邓超','0000000',2,'1981-11-04','13689674534','杭州市西湖区市委家属院10号楼',3,1,'2016-07-11 08:02:47',NULL,NULL),(14,'yangguo','杨过','0000000',2,'1980-01-01','13388886623','杭州市滨江区北苑家园茉莉园20号楼',3,1,'2015-02-01 03:52:07',NULL,NULL),(15,'zhaomin','赵敏','0000000',1,'1987-12-04','18099897657','杭州市江干区天通苑3区12号楼',2,1,'2015-09-12 12:02:12',NULL,NULL);
/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;
```
### 2 spring boot && vscode
- 2.1 java环境：
  - 2.1.1 首先下载安装java se： [https://javadl.oracle.com/webapps/download/AutoDL?BundleId=245029_d3c52aa6bfa54d3ca74e617f18309292](https://javadl.oracle.com/webapps/download/AutoDL?BundleId=245029_d3c52aa6bfa54d3ca74e617f18309292)
  - 2.1.2 下载jdk11： [https://github-releases.githubusercontent.com/372924883/f3dd1529-363d-49fe-b053-028ff6518a3f?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Credential=AKIAIWNJYAX4CSVEH53A%2F20210825%2Fus-east-1%2Fs3%2Faws4_request&X-Amz-Date=20210825T074918Z&X-Amz-Expires=300&X-Amz-Signature=d6ad0306c61908e94fc54fee6ae1c332e524603c13c8dcdd0e1ddcefe37d7aa9&X-Amz-SignedHeaders=host&actor_id=40788136&key_id=0&repo_id=372924883&response-content-disposition=attachment%3B%20filename%3DOpenJDK11U-jdk_x64_windows_hotspot_11.0.12_7.msi&response-content-type=application%2Foctet-stream](https://github-releases.githubusercontent.com/372924883/f3dd1529-363d-49fe-b053-028ff6518a3f?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Credential=AKIAIWNJYAX4CSVEH53A%2F20210825%2Fus-east-1%2Fs3%2Faws4_request&X-Amz-Date=20210825T074918Z&X-Amz-Expires=300&X-Amz-Signature=d6ad0306c61908e94fc54fee6ae1c332e524603c13c8dcdd0e1ddcefe37d7aa9&X-Amz-SignedHeaders=host&actor_id=40788136&key_id=0&repo_id=372924883&response-content-disposition=attachment%3B%20filename%3DOpenJDK11U-jdk_x64_windows_hotspot_11.0.12_7.msi&response-content-type=application%2Foctet-stream)
  - 2.1.3 配置jdk的位置：JAVA_HOME: Z:\BASE_ENV\java\openJDK11\
- 2.2 ide： vscode
  - 2.2.1 参考其中之一：[https://spring.io/tools](https://spring.io/tools)
  - 2.2.2 安装两个插件： vscjava.vscode-java-pack pivotal.vscode-boot-dev-pack
  - 然后按照插件开始工作
- 2.3 build tool: maven配置方式：
  - 2.3.1 手动下载：[https://mirrors.tuna.tsinghua.edu.cn/apache/maven/maven-3/3.8.2/binaries/apache-maven-3.8.2-bin.tar.gz](https://mirrors.tuna.tsinghua.edu.cn/apache/maven/maven-3/3.8.2/binaries/apache-maven-3.8.2-bin.tar.gz)
  - 2.3.2 配置第三方jar包和jar包的目录以及个人的maven配置：
    - 以idea为例子： build->build tools->maven->user settings: Z:\softwares\apache-maven-3.6.3\conf\settings.xml, 打开这个可以看到这里有jar包的获取的mirror等。
    - build->build tools->maven->local repo: Z:\softwares\repo, repo存放了生成的jar包以及第三方jar包
## 2021/08/27
### 1 liquibase的changelog自动生成：
进入对应的模块的根目录，（也就是含有pom.xml的目录）执行如下命令：
```sh
mvn liquibase:generateChangeLog
```
### 2 liquibase changelog validation failed:
同上，执行：
```
mvn liquibase:clearCheckSums
```
## 2021/08/28
### 1 java spring框架中的几个关键概念的理解：
- 0 ioc (控制翻转)：对象的生命周期不再由程序员维护，而是交给框架维护
- 1 spring的容器理解：bean的管理者，比如spring中的两种容器[Spring BeanFactory 容器](https://www.w3cschool.cn/wkspring/j3181mm3.html)和[Spring ApplicationContext 容器](https://www.w3cschool.cn/wkspring/yqdx1mm5.html)，他们返回的是一个bean的工(这大概就是容器)，我们可以通过这个工厂获得这个bean。 这里有一个图很生动： ![https://atts.w3cschool.cn/attachments/image/wk/wkspring/ioc1.jpg](https://atts.w3cschool.cn/attachments/image/wk/wkspring/ioc1.jpg)
- 2 bean的理解：[https://www.w3cschool.cn/wkspring/8kei1icc.html](https://www.w3cschool.cn/wkspring/8kei1icc.html)
  - 其实主要就是说，bean本身代表的是被spring框架管理起来的对象，它的创建生成可以通过spring core提供的函数来生成，spring管理它的时候需要bean对应的xml，里面确定了它的依赖，构造，析构等等函数。
  - 管理过程如图： ![](https://atts.w3cschool.cn/attachments/image/20201030/1604037368126454.png)
- 3 DI(依赖注入) spring的核心功能，通过di来管理bean之间的依赖关系 
  - [构造函数注入](https://www.w3cschool.cn/wkspring/t7n41mm7.html)实际上就是xml中声明构造里需要相对应的依赖类，下面的都是类似的
  - [setter注入](https://www.w3cschool.cn/wkspring/vneb1mm9.html) 实际上就是，调用类有一个setter方法，会将调用类的一个手续属性setter成为对应的被调用类，然后再xml中配置好这个setter方法对应的被调用类即可
  - [注入内部bean](https://www.w3cschool.cn/wkspring/qujn1icm.html) 实际上就是假设调用类中有一个属性是一个依赖类需要初始化，那么直接在bean的xml为这个属性内部嵌套一个bean
  - [注入集合] 就是在xml中给调用类的一些属性初始化，没什么意思
- 4 beans自动装配: 也就是不使用上面DI中在xml配置文件中的<constructor-arg>和<property>元素来注入，而是自动装配来减少xml的大小，自动装配有几种模式：
  - 4.1 byName: 调用类里有一个属性的定义名称是A,那么spring会在xml找到A这个bean，也就是A的这个bean的id需要和A相等，然后完成装配
  - 4.2 byType: 调用类里有一个属性的类型为A,那么spring会在xml找到A这个bean，也就会说A的这个bean的class需要和A相等，然后完成装配
  - 4.3 构造自动装配: 就是构造函数中的参数去做byType的自动装配
- 5 基于注解的配置(spring2.5 以后就可以使用注解来做依赖注入，这样就不需要使用xml来描述哪两个bean之间有依赖了)
  - 5.1 @Reuired 会告诉spring调用类的属性的set方法(这个set方法被@required了，必须在xml中配置这个属性的依赖
  - 5.2 @Autowired 自动把bean装配到调用类的属性里，可以申明给属性或者构造函数甚至set，map等属性
  - 5.3 @qualifier 就是你的xml中有多个bean的class是一样的，然后你得显示的告诉spring你需要用哪个id的bean装配到调用类的用autowird注解的字段里吧？那就使用@qualifier来明确使用哪个id即可
  - 5.4 JSR250: [@PostConstruct](https://docs.oracle.com/javaee/7/api/javax/annotation/PostConstruct.html)，@PreDestroy和xml中的或或者@bean语法中的init—method和destroy-method类似，都是在javabean在被注入以后需要调用的函数，然后只能有一个函数被这样注释，其次，@Resource则是在字段或者setter方法中告诉spring在调用类中去注入哪一个id的bean
  - 5.5 基于java的配置，@configuration：表示这个类可以使用容器作为bean定义的来源，@bean:注释的方法会返回一个对象，对象是被注册在spring 应用程序的上下文的bean，也就是说，configuration注释的类相当于xml中的bean的class，而@Bean注释的方法，相当于xml中bean的id.
  - 5.6 [spring事件处理](https://www.w3cschool.cn/wkspring/reap1icq.html)，spring通过contextaplication来管理beaan的生命周期，那么这个context类有start，stop等过程，然后可以在xml中告诉spring start和stop过程分别调用哪些函数，这就达到了上下文发布和暂停时执行某些动作的目的
  - 5.7 [spring自定义事件](https://www.w3cschool.cn/wkspring/7jho1ict.html), 主要是定义一个even，然后有个custompublisher继承自框架的publisher，然后有个handler继承自框架的handler，那么publisher发布的时候，handler就会自动想要相对于这个event的handle方法，完成事件的响应过程
- 
### 2 spring boot **最全文档： [https://docs.spring.io/spring-boot/docs/2.1.6.RELEASE/reference/html/](https://docs.spring.io/spring-boot/docs/2.1.6.RELEASE/reference/html/)**
#### 2.1 关键概念
#### 2.2
## 2021 09/10
### 1 cesium/source/core/cartesian3.js 经纬度转WGS84坐标代码：
```js
Cartesian3.fromRadians = function (
  longitude,
  latitude,
  height,
  ellipsoid,
  result
) {
  //>>includeStart('debug', pragmas.debug);
  Check.typeOf.number("longitude", longitude);
  Check.typeOf.number("latitude", latitude);
  //>>includeEnd('debug');
  height = defaultValue(height, 0.0);
  var radiiSquared = defined(ellipsoid)
    ? ellipsoid.radiiSquared
    : wgs84RadiiSquared;
  var cosLatitude = Math.cos(latitude);
  scratchN.x = cosLatitude * Math.cos(longitude);
  scratchN.y = cosLatitude * Math.sin(longitude);
  scratchN.z = Math.sin(latitude);
  scratchN = Cartesian3.normalize(scratchN, scratchN);
  Cartesian3.multiplyComponents(radiiSquared, scratchN, scratchK);
  var gamma = Math.sqrt(Cartesian3.dot(scratchN, scratchK));
  scratchK = Cartesian3.divideByScalar(scratchK, gamma, scratchK);
  scratchN = Cartesian3.multiplyByScalar(scratchN, height, scratchN);
  if (!defined(result)) {
    result = new Cartesian3();
  }
  return Cartesian3.add(scratchK, scratchN, result);
};
```
### 1 redis [持久化方式](http://www.redis.cn/topics/persistence.html)
- RDB (redis database backup file)
- AOF (append only file)
### 2 sql的生成方式
## 2021/09/16 
Active 3D Modeling via Online Multi-View Stereo
[11] M. Pizzoli, C. Forster, and D. Scaramuzza, “Remode: Probabilistic,
monocular dense reconstruction in real time,” in 2014 IEEE International Conference on Robotics and Automation (ICRA)
[37] J. R. Shewchuk, “Delaunay refinement algorithms for triangular mesh
generation,” Computational Geometry, vol. 22, no. 1-3, pp. 21–74,
[14] T. Whelan, R. F. Salas-Moreno, B. Glocker, A. J. Davison, and
S. Leutenegger, “Elasticfusion: Real-time dense slam and light source
estimation,” The International Journal of Robotics Research, vol. 35,
no. 14, pp. 1697–1716, 2016.
## 2021/09/23
- 1 提出了什么？
- 2 解决了什么问题？
- 3 关键思路？


## 2022/06/15

