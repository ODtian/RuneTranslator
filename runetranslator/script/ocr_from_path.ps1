using namespace Windows.Storage
using namespace Windows.Graphics.Imaging

Param(
    [string]$Path = $(throw "Parameter missing: -Path Path"),
    [string]$Lang = $(throw "Parameter missing: -Lang Lang")
)

Begin {
    [Console]::OutputEncoding = [Text.UTF8Encoding]::UTF8
    Add-Type -AssemblyName System.Runtime.WindowsRuntime

    $null = [Windows.Storage.StorageFile, Windows.Storage, ContentType = WindowsRuntime]
    $null = [Windows.Media.Ocr.OcrEngine, Windows.Foundation, ContentType = WindowsRuntime]
    $null = [Windows.Foundation.IAsyncOperation`1, Windows.Foundation, ContentType = WindowsRuntime]
    $null = [Windows.Graphics.Imaging.SoftwareBitmap, Windows.Foundation, ContentType = WindowsRuntime]
    $null = [Windows.Storage.Streams.RandomAccessStream, Windows.Storage.Streams, ContentType = WindowsRuntime]

    $ocrEngine = [Windows.Media.Ocr.OcrEngine]::TryCreateFromLanguage($Lang)
    $getAwaiterBaseMethod = [WindowsRuntimeSystemExtensions].GetMember('GetAwaiter').
    Where( {
            $PSItem.GetParameters()[0].ParameterType.Name -eq 'IAsyncOperation`1'
        }, 'First')[0]

    Function Await {
        param($AsyncTask, $ResultType)

        $getAwaiterBaseMethod.
        MakeGenericMethod($ResultType).
        Invoke($null, @($AsyncTask)).
        GetResult()
    }   
}

Process {
    $Path = $ExecutionContext.SessionState.Path.GetUnresolvedProviderPathFromPSPath($Path)

    $params = @{ 
        AsyncTask  = [StorageFile]::GetFileFromPathAsync($Path)
        ResultType = [StorageFile]
    }
    $storageFile = Await @params


    $params = @{ 
        AsyncTask  = $storageFile.OpenAsync([FileAccessMode]::Read)
        ResultType = [Streams.IRandomAccessStream]
    }
    $fileStream = Await @params


    $params = @{
        AsyncTask  = [BitmapDecoder]::CreateAsync($fileStream)
        ResultType = [BitmapDecoder]
    }
    $bitmapDecoder = Await @params

    $params = @{ 
        AsyncTask  = $bitmapDecoder.GetSoftwareBitmapAsync()
        ResultType = [SoftwareBitmap]
    }
    $softwareBitmap = Await @params
    
    # Run the OCR
    $params = @{ 
        AsyncTask  = $ocrEngine.RecognizeAsync($softwareBitmap)
        ResultType = ([Windows.Media.Ocr.OcrResult])
    }
    $result = Await @params
    $result | ConvertTo-Json -Compress -Depth 5
}
