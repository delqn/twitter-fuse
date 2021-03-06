def make_notebook(tweets):
    string1 = ''
    string2 = ''
    suffix1 = ', ",", " ", '
    suffix2 = ', ",", '
    for tweet in tweets:
        string1 += '"\\"\\<' + tweet + '\\>\\""' + suffix1
        string2 += '"\\<\\"' + tweet + '\\"\\>"' + suffix2

    string1 = string1[:-len(suffix1)]
    string2 = string2[:-len(suffix2)]
    return bytes('''(* Content-type: application/vnd.wolfram.mathematica *)

(*** Wolfram Notebook File ***)
(* http://www.wolfram.com/nb *)

(* CreatedBy='Mathematica 10.4' *)

(*CacheID: 234*)
(* Internal cache information:
NotebookFileLineBreakTest
NotebookFileLineBreakTest
NotebookDataPosition[       158,          7]
NotebookDataLength[      1334,         54]
NotebookOptionsPosition[      1008,         37]
NotebookOutlinePosition[      1369,         53]
CellTagsIndexPosition[      1326,         50]
WindowFrame->Normal*)

(* Beginning of Notebook Content *)
Notebook[{

Cell[CellGroupData[{
Cell[BoxData[
 RowBox[{"list", " ", "=", " ",
  RowBox[{"{",
   RowBox[{
   ''' + string1 + '''}],
    "}"}]}]], "Input",
 CellChangeTimes->{{3.666923361835514*^9, 3.666923371842855*^9}}],

Cell[BoxData[
 RowBox[{"{",
  RowBox[{''' + string2 + '''}],
  "}"}]], "Output",
 CellChangeTimes->{3.666923373081665*^9}]
}, Open  ]]
},
WindowSize->{Full, Full},
WindowMargins->{{236, Automatic}, {Automatic, 50}},
FrontEndVersion->"10.4 for Mac OS X x86 (32-bit, 64-bit Kernel) (February 25, \\
2016)",
StyleDefinitions->"Default.nb"
]
(* End of Notebook Content *)

(* Internal cache information *)
(*CellTagsOutline
CellTagsIndex->{}
*)
(*CellTagsIndex
CellTagsIndex->{}
*)
(*NotebookFileOutline
Notebook[{
Cell[CellGroupData[{
Cell[580, 22, 242, 6, 28, "Input"],
Cell[825, 30, 167, 4, 62, "Output"]
}, Open  ]]
}
]
*)
''')
