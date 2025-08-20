Attribute VB_Name = "Module1"
Option Explicit

'''<summary>
'''モジュールの説明
'''</summary>

Sub procedureWithoutDocComment()
    Debug.Print "procedure without doc comment running."
End Sub

'''<summary>
'''かんたんなプロシージャ
'''</summary>
Sub sampleProcedure()
    Debug.Print "sampleProcedure running."
End Sub

'''<summary>
'''かんたんなプライベートプロシージャ
'''</summary>
'''<param name="Num">数字</param>
Private Sub samplePrivateProcedure(ByVal num As Integer)
    Debug.Print num
End Sub

''' <summary>
''' 名前を呼ぶ文字列を返す関数
''' 名前を入力すると「こんにちは、○○さん」を出力する。
''' </summary>
''' <param name="name">名前</param>
''' <returns>名前を呼ぶ文字列</returns>
''' <remarks>
''' 注意事項1
''' 注意事項2
''' </remarks>
''' <remarks>注意事項3</remarks>
Function sampleFunction(ByVal name As String) As String
    Dim callName As String
    callName = name + "さん"
    Debug.Print "こんにちは、" + callName
    sampleFunction = callName
End Function

''' <summary>
''' 修正確認用
''' </summary>
''' <param name="name">名前</param>
''' <remarks>注意事項</remarks>
Sub testFix(ByVal name)
    Debug.Print "こんにちは。"
End Sub

''' <summary>
''' 修正確認用2
''' </summary>
''' <param name="name">名前</param>
''' <remarks>注意事項</remarks>
Sub testFix2(name)
    Debug.Print "こんにちは。"
End Sub
