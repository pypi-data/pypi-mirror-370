do { my $x = {
  'abi' => {
    'default_abi' => '2',
    'efi64' => '3',
    'gnuw64' => '4',
    'unix64' => '2',
    'win64' => '3'
  },
  'header' => {
    'alloca.h' => 1,
    'complex.h' => 1,
    'dlfcn.h' => 1,
    'inttypes.h' => 1,
    'limits.h' => 1,
    'psapi.h' => 0,
    'signal.h' => 1,
    'stdbool.h' => 1,
    'stddef.h' => 1,
    'stdint.h' => 1,
    'stdio.h' => 1,
    'stdlib.h' => 1,
    'string.h' => 1,
    'sys/cygwin.h' => 0,
    'sys/stat.h' => 1,
    'sys/types.h' => 1,
    'unistd.h' => 1,
    'wchar.h' => 1,
    'windows.h' => 0
  },
  'probe' => {
    'abi' => 1,
    'alloca' => 1,
    'complex' => 1,
    'longdouble' => 1,
    'recordvalue' => 1,
    'strnlen' => 1,
    'variadic' => 1
  },
  'type' => {
    '_Bool' => {
      'align' => '1',
      'sign' => 'unsigned',
      'size' => '1'
    },
    'blkcnt_t' => {
      'align' => '8',
      'sign' => 'signed',
      'size' => '8'
    },
    'blksize_t' => {
      'align' => '8',
      'sign' => 'signed',
      'size' => '8'
    },
    'bool' => {
      'align' => '1',
      'sign' => 'unsigned',
      'size' => '1'
    },
    'char' => {
      'align' => '1',
      'sign' => 'signed',
      'size' => '1'
    },
    'dev_t' => {
      'align' => '8',
      'sign' => 'unsigned',
      'size' => '8'
    },
    'double' => {
      'align' => '8',
      'size' => '8'
    },
    'double complex' => {
      'align' => '8',
      'size' => '16'
    },
    'enum' => {
      'align' => '4',
      'sign' => 'unsigned',
      'size' => '4'
    },
    'float' => {
      'align' => '4',
      'size' => '4'
    },
    'float complex' => {
      'align' => '4',
      'size' => '8'
    },
    'gid_t' => {
      'align' => '4',
      'sign' => 'unsigned',
      'size' => '4'
    },
    'ino_t' => {
      'align' => '8',
      'sign' => 'unsigned',
      'size' => '8'
    },
    'int' => {
      'align' => '4',
      'sign' => 'signed',
      'size' => '4'
    },
    'int16_t' => {
      'align' => '2',
      'sign' => 'signed',
      'size' => '2'
    },
    'int32_t' => {
      'align' => '4',
      'sign' => 'signed',
      'size' => '4'
    },
    'int64_t' => {
      'align' => '8',
      'sign' => 'signed',
      'size' => '8'
    },
    'int8_t' => {
      'align' => '1',
      'sign' => 'signed',
      'size' => '1'
    },
    'intmax_t' => {
      'align' => '8',
      'sign' => 'signed',
      'size' => '8'
    },
    'intptr_t' => {
      'align' => '8',
      'sign' => 'signed',
      'size' => '8'
    },
    'long' => {
      'align' => '8',
      'sign' => 'signed',
      'size' => '8'
    },
    'long double' => {
      'align' => '16',
      'size' => '16'
    },
    'long double complex' => {
      'align' => '16',
      'size' => '32'
    },
    'long long' => {
      'align' => '8',
      'sign' => 'signed',
      'size' => '8'
    },
    'mode_t' => {
      'align' => '4',
      'sign' => 'unsigned',
      'size' => '4'
    },
    'nlink_t' => {
      'align' => '8',
      'sign' => 'unsigned',
      'size' => '8'
    },
    'off_t' => {
      'align' => '8',
      'sign' => 'signed',
      'size' => '8'
    },
    'pointer' => {
      'align' => '8',
      'size' => '8'
    },
    'ptrdiff_t' => {
      'align' => '8',
      'sign' => 'signed',
      'size' => '8'
    },
    'senum' => {
      'align' => '4',
      'sign' => 'signed',
      'size' => '4'
    },
    'short' => {
      'align' => '2',
      'sign' => 'signed',
      'size' => '2'
    },
    'signed char' => {
      'align' => '1',
      'sign' => 'signed',
      'size' => '1'
    },
    'signed int' => {
      'align' => '4',
      'sign' => 'signed',
      'size' => '4'
    },
    'signed long' => {
      'align' => '8',
      'sign' => 'signed',
      'size' => '8'
    },
    'signed long long' => {
      'align' => '8',
      'sign' => 'signed',
      'size' => '8'
    },
    'signed short' => {
      'align' => '2',
      'sign' => 'signed',
      'size' => '2'
    },
    'size_t' => {
      'align' => '8',
      'sign' => 'unsigned',
      'size' => '8'
    },
    'ssize_t' => {
      'align' => '8',
      'sign' => 'signed',
      'size' => '8'
    },
    'time_t' => {
      'align' => '8',
      'sign' => 'signed',
      'size' => '8'
    },
    'uid_t' => {
      'align' => '4',
      'sign' => 'unsigned',
      'size' => '4'
    },
    'uint16_t' => {
      'align' => '2',
      'sign' => 'unsigned',
      'size' => '2'
    },
    'uint32_t' => {
      'align' => '4',
      'sign' => 'unsigned',
      'size' => '4'
    },
    'uint64_t' => {
      'align' => '8',
      'sign' => 'unsigned',
      'size' => '8'
    },
    'uint8_t' => {
      'align' => '1',
      'sign' => 'unsigned',
      'size' => '1'
    },
    'uintmax_t' => {
      'align' => '8',
      'sign' => 'unsigned',
      'size' => '8'
    },
    'uintptr_t' => {
      'align' => '8',
      'sign' => 'unsigned',
      'size' => '8'
    },
    'unsigned char' => {
      'align' => '1',
      'sign' => 'unsigned',
      'size' => '1'
    },
    'unsigned int' => {
      'align' => '4',
      'sign' => 'unsigned',
      'size' => '4'
    },
    'unsigned long' => {
      'align' => '8',
      'sign' => 'unsigned',
      'size' => '8'
    },
    'unsigned long long' => {
      'align' => '8',
      'sign' => 'unsigned',
      'size' => '8'
    },
    'unsigned short' => {
      'align' => '2',
      'sign' => 'unsigned',
      'size' => '2'
    },
    'wchar_t' => {
      'align' => '4',
      'sign' => 'signed',
      'size' => '4'
    },
    'wint_t' => {
      'align' => '4',
      'sign' => 'unsigned',
      'size' => '4'
    }
  }
};
$x;}