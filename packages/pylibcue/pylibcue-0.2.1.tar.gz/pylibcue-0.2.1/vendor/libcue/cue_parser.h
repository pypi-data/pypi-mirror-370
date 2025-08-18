/* A Bison parser, made by GNU Bison 3.8.2.  */

/* Bison interface for Yacc-like parsers in C

   Copyright (C) 1984, 1989-1990, 2000-2015, 2018-2021 Free Software Foundation,
   Inc.

   This program is free software: you can redistribute it and/or modify
   it under the terms of the GNU General Public License as published by
   the Free Software Foundation, either version 3 of the License, or
   (at your option) any later version.

   This program is distributed in the hope that it will be useful,
   but WITHOUT ANY WARRANTY; without even the implied warranty of
   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
   GNU General Public License for more details.

   You should have received a copy of the GNU General Public License
   along with this program.  If not, see <https://www.gnu.org/licenses/>.  */

/* As a special exception, you may create a larger work that contains
   part or all of the Bison parser skeleton and distribute that work
   under terms of your choice, so long as that work isn't itself a
   parser generator using the skeleton or a modified version thereof
   as a parser skeleton.  Alternatively, if you modify or redistribute
   the parser skeleton itself, you may (at your option) remove this
   special exception, which will cause the skeleton and the resulting
   Bison output files to be licensed under the GNU General Public
   License without this special exception.

   This special exception was added by the Free Software Foundation in
   version 2.2 of Bison.  */

/* DO NOT RELY ON FEATURES THAT ARE NOT DOCUMENTED in the manual,
   especially those whose name start with YY_ or yy_.  They are
   private implementation details that can be changed or removed.  */

#ifndef YY_YY_VENDOR_LIBCUE_CUE_PARSER_H_INCLUDED
# define YY_YY_VENDOR_LIBCUE_CUE_PARSER_H_INCLUDED
/* Debug traces.  */
#ifndef YYDEBUG
# define YYDEBUG 0
#endif
#if YYDEBUG
extern int yydebug;
#endif

/* Token kinds.  */
#ifndef YYTOKENTYPE
# define YYTOKENTYPE
  enum yytokentype
  {
    YYEMPTY = -2,
    YYEOF = 0,                     /* "end of file"  */
    YYerror = 256,                 /* error  */
    YYUNDEF = 257,                 /* "invalid token"  */
    NUMBER = 258,                  /* NUMBER  */
    STRING = 259,                  /* STRING  */
    CATALOG = 260,                 /* CATALOG  */
    CDTEXTFILE = 261,              /* CDTEXTFILE  */
    FFILE = 262,                   /* FFILE  */
    BINARY = 263,                  /* BINARY  */
    MOTOROLA = 264,                /* MOTOROLA  */
    AIFF = 265,                    /* AIFF  */
    WAVE = 266,                    /* WAVE  */
    MP3 = 267,                     /* MP3  */
    FLAC = 268,                    /* FLAC  */
    TRACK = 269,                   /* TRACK  */
    AUDIO = 270,                   /* AUDIO  */
    MODE1_2048 = 271,              /* MODE1_2048  */
    MODE1_2352 = 272,              /* MODE1_2352  */
    MODE2_2336 = 273,              /* MODE2_2336  */
    MODE2_2048 = 274,              /* MODE2_2048  */
    MODE2_2342 = 275,              /* MODE2_2342  */
    MODE2_2332 = 276,              /* MODE2_2332  */
    MODE2_2352 = 277,              /* MODE2_2352  */
    TRACK_ISRC = 278,              /* TRACK_ISRC  */
    FLAGS = 279,                   /* FLAGS  */
    PRE = 280,                     /* PRE  */
    DCP = 281,                     /* DCP  */
    FOUR_CH = 282,                 /* FOUR_CH  */
    SCMS = 283,                    /* SCMS  */
    PREGAP = 284,                  /* PREGAP  */
    INDEX = 285,                   /* INDEX  */
    POSTGAP = 286,                 /* POSTGAP  */
    TITLE = 287,                   /* TITLE  */
    PERFORMER = 288,               /* PERFORMER  */
    SONGWRITER = 289,              /* SONGWRITER  */
    COMPOSER = 290,                /* COMPOSER  */
    ARRANGER = 291,                /* ARRANGER  */
    MESSAGE = 292,                 /* MESSAGE  */
    DISC_ID = 293,                 /* DISC_ID  */
    GENRE = 294,                   /* GENRE  */
    TOC_INFO1 = 295,               /* TOC_INFO1  */
    TOC_INFO2 = 296,               /* TOC_INFO2  */
    UPC_EAN = 297,                 /* UPC_EAN  */
    ISRC = 298,                    /* ISRC  */
    SIZE_INFO = 299,               /* SIZE_INFO  */
    DATE = 300,                    /* DATE  */
    XXX_GENRE = 301,               /* XXX_GENRE  */
    REPLAYGAIN_ALBUM_GAIN = 302,   /* REPLAYGAIN_ALBUM_GAIN  */
    REPLAYGAIN_ALBUM_PEAK = 303,   /* REPLAYGAIN_ALBUM_PEAK  */
    REPLAYGAIN_TRACK_GAIN = 304,   /* REPLAYGAIN_TRACK_GAIN  */
    REPLAYGAIN_TRACK_PEAK = 305    /* REPLAYGAIN_TRACK_PEAK  */
  };
  typedef enum yytokentype yytoken_kind_t;
#endif

/* Value type.  */
#if ! defined YYSTYPE && ! defined YYSTYPE_IS_DECLARED
union YYSTYPE
{

	long ival;
	char *sval;


};
typedef union YYSTYPE YYSTYPE;
# define YYSTYPE_IS_TRIVIAL 1
# define YYSTYPE_IS_DECLARED 1
#endif


extern YYSTYPE yylval;


int yyparse (void);


#endif /* !YY_YY_VENDOR_LIBCUE_CUE_PARSER_H_INCLUDED  */
