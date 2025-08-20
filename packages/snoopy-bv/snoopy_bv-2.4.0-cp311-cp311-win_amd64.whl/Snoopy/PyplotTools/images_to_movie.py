import os
import numpy as np
import matplotlib.pyplot as plt
from Snoopy import logger
from scipy.interpolate import InterpolatedUnivariateSpline
from tqdm import tqdm

def video_overlay( movieFile, ts , offset = 0.0 , output = "movies", output_type = "movie_and_pictures", skip_existing_pics = False, fps = 25):
    """Plot time-series, overlayed with picture from videos.

    Keep all frames from original movie.

    Parameters
    ----------
    movieFile : str
        Path to the video file.
    ts : pd.Series
        Time-series to plot.
    offset : float, optional
        Offset between video and time-series, if any. The default is 20.0.
    output : str, optional
        Output folder for pictures, the generated movies is output one level higher. The default is "movies".
    output_type : str, optional, default to "movie_and_pictures"
        If movie_and_pictures, pictures are converted to movie and kept. If "movie", pictures are removed.
    skip_existing_pics : bool, optional, default to False
        If True, picture are not generated if file already exists.



    Returns
    -------
    list(str)
        List of picture file created
    """

    import cv2

    # Copy to not modify the time-serie that might be used elsewhere
    ts_ = ts.copy()
    ts_.index += offset

    if not os.path.exists(output) :
        os.makedirs( output )

    if not os.path.exists(movieFile):
        raise(Exception( f"{movieFile:}" ))

    cap = cv2.VideoCapture(movieFile)

    n_frames_tot = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    width  = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

    fps = cap.get(cv2.CAP_PROP_FPS)

    movie_duration = n_frames_tot / fps
    
    
    my_dpi = 100
    fig, ax = plt.subplots(1,1, figsize=(width/my_dpi, height/my_dpi), dpi=my_dpi*2)

    tstart = ts_.index[0]
    tstop = ts_.index[-1]
    iframe_start = int(tstart * fps)
    iframe_stop = int(tstop * fps)

    n_frames = iframe_stop - iframe_start

    logger.info( f"{width:} {n_frames:}/{n_frames_tot:}  {fps:} {movie_duration:}" )

    cap.set(cv2.CAP_PROP_POS_FRAMES, iframe_start)

    interp = InterpolatedUnivariateSpline(ts_.index.values, ts_.values)

    ybounds = [ts_.min()*1.1,  ts_.max()*1.1]

    fileList = []
    for i in tqdm(list(range(iframe_start, iframe_stop )), desc = movieFile):

        outfig = f"{output:}/pic_{i-iframe_start:03}.png"
        flag, frame = cap.read()

        if skip_existing_pics and os.path.exists(outfig) :
            logger.info(f"Skipping {outfig:}")
            continue

        t = i / fps

        fig.clf()
        ax = fig.add_subplot()
        ax.grid(False)
        ax.set_xticks([])
        ax.set_yticks([])

        ax2 = ax.twinx().twiny()
        ax2.xaxis.tick_bottom()
        ax2.xaxis.set_label_position("bottom")
        ax2.yaxis.set_ticks_position("left")
        ax2.set_title( f"t = {t:.2f}" )

        ax2.set( ylim = ybounds, xlabel = "time(s)" )

        ax.imshow( np.flip(frame, axis=-1)  ) # The flip is the convertion RGB / BGR (difference convention in cv2 and matplotlib)
        ax2.plot( ts_.index.values, ts_.values, linestyle = "-" , linewidth = 2, color = "orange")

        y=interp(t)
        ax2.plot( t , y, marker= "s", linestyle = "")

        fig.savefig( outfig )

        fileList.append(outfig)

    if "movie" in output_type :
        pictures_2_movie( pictures = fileList , output = output, engine = "cv2", cleanPictures = not "picture" in output_type, fps = fps )

    return fileList


def concat_frames(  frames, nrows = 2, ncols = 1, workingFrame = None ):
    """Concatenate frames. For now, assumes same dimension for all frames.

    Parameters
    ----------
    frames : List( np.ndarray(h,w,3 or 4)).
        List of pictures as float array.
    nrows : int, optional
        Number of rows. The default is 2.
    ncols : int, optional
        Number of columns. The default is 1.

    Returns
    -------
    np.ndarray
       Concatenated frame
    """

    if workingFrame is None :
        workingFrame = _create_workingFrame(frames, nrows, ncols)

    n = len(frames)

    if (n == 2) :
        h1, w1, dim = frames[0].shape
        h2, w2, dim = frames[1].shape
        if (nrows == 2):
            workingFrame[:h1,:,:] = frames[0]
            workingFrame[h1:,:,:] = frames[1]
        else:
            workingFrame[:h1,:,:] = frames[0]
            workingFrame[h1:,:,:] = frames[1]

    if n in (3,4) and nrows == 2 :
        h, w, dim = frames[0].shape
        workingFrame[:h,:w,:] = frames[0]
        workingFrame[h:,:w,:] = frames[1]
        workingFrame[:h,w:,:] = frames[2]
        if n == 4 :
            workingFrame[h:,w:,:] = frames[3]

    return workingFrame


def concat_pictures( input_files, output_file,  **kwargs ):
    from PIL import Image
    frames = [ np.asarray(Image.open(d)) for d in input_files ]
    im = Image.fromarray( concat_frames( frames ,  **kwargs)  )
    im.save(output_file)
    return 



def _create_workingFrame( frames, nrows , ncols ):
    hList = [ frame.shape[0] for frame in frames ]
    wList = [ frame.shape[1] for frame in frames ]
    dim = frames[0].shape[-1]
    h,w = _get_concatanated_size( hList, wList, nrows, ncols  )
    workingFrame = np.empty( (h , w, dim) , dtype = frames[0].dtype )
    return workingFrame

def _get_concatanated_size( hList, wList, nrows, ncols ) :
    n = len(hList)
    if (n == 2) :
        if (nrows == 2):
            return ( np.sum(hList) , np.max(wList) )
        else:
            return ( np.max(hList) , np.sum(wList) )
    if n in (3,4) and nrows == 2 :
        return ( np.max(hList)*2 , np.max(wList)*2 )



def concatenate_video( videos, nrows, ncols, output ) :
    """Concatenates video (spatially). Creates array of videos.

    Parameters
    ----------
    videos : List(str)
        List of video files
    nrows : int, optional
        Number of rows. The default is 2.
    ncols : int, optional
        Number of columns. The default is 1.

    Returns
    -------
    None.
    """

    import cv2

    caps = [cv2.VideoCapture( v ) for v in videos]

    n_framesList = [ int(cap.get(cv2.CAP_PROP_FRAME_COUNT)) for cap in caps ]

    n_frame = np.min(n_framesList)

    fps = caps[0].get(cv2.CAP_PROP_FPS)

    fourcc = cv2.VideoWriter_fourcc(*'XVID') # Getting h264 to work here is a bit random

    # Create videoWriter with correct dimension
    hList = [ int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT)) for cap in caps ]
    wList = [ int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)) for cap in caps ]
    h, w = _get_concatanated_size(hList, wList , nrows, ncols)
    video = cv2.VideoWriter( f"{output:}.mp4", fourcc, fps, (w, h )  )

    for i in tqdm(list(range(n_frame)), desc = "Concatenate videos") :
       frames = [ cap.read()[1] for cap in caps ]
       if i == 0 :
           workingFrame = _create_workingFrame(frames, nrows, ncols)
       newFrame = concat_frames(frames, nrows = nrows, ncols = ncols, workingFrame = workingFrame)
       video.write(newFrame)

    cv2.destroyAllWindows()
    video.release()



def pictures_2_movie( pictures = "pic_%03d.png", output = "movie",  ffmpeg_path = "ffmpeg", cleanPictures = True, engine = "cv2", fps = 25, cv2_codec = "X264" ):
    """Concatenate picture in a movie (simply call ffmpeg or opencv2 with correct argument and decent default codec)

    Parameters
    ----------
    pattern : str, optional
        Picture pattern. The default is "pic_%03d.png".
    output : str, optional
        Base name of the movie file (extension .mp4 will be added). The default is "movie".
    ffmpeg_path : str, optional
        Path to ffmeg executable. The default is "ffmpeg".
    engine : str, optional
        "cv2" or "ffmpeg".

    Returns
    -------
    None.

    Note
    ----
    For now, pattern works with ffmpeg engine, while explicit file list works only with cv2.
    """
    if engine == "ffmeg":
        if isinstance(pictures, str) :
            os.system(f"{ffmpeg_path:} -y -i {pictures} -c:v libx264 -vf fps=25 -pix_fmt yuv420p {output:}.mp4")
        elif hasattr(pictures, "__iter__") :
            # Does not work.
            raise(Exception("pictures_2_movie does not work yet with file list and ffmpeg engine. Try engine='cv2'"))
            with open("tmp.txt", "w") as f :
                for p in pictures :
                    f.write( f"file {p:}\n" )
            os.system(f"{ffmpeg_path:} -y -f concat -safe 0 -i tmp.txt -c:v libx264 -vf fps={fps:} -pix_fmt yuv420p {output:}.mp4")
    else :
        if isinstance(pictures, str) :
            raise(Exception( "pictures_2_movie does not work yet with file pattern and cv2 engine. Try engine='cv2'"))
        import cv2

        exists_ = np.array([os.path.exists( p ) for p in pictures]).astype(int)
        if not np.all( exists_ ) : 
            raise(Exception( f"{pictures[~exists_]:} cannot be found" ) )

        fourcc = cv2.VideoWriter_fourcc(*cv2_codec)
        # fourcc = cv2.VideoWriter_fourcc(*'XVID') # Getting h264 to work here is a bit random
        frame = cv2.imread( pictures[0] )
        height, width, layers = frame.shape
        video = cv2.VideoWriter( f"{output:}.mkv", fourcc, fps, (width,height))
        for image in tqdm(pictures, desc = "Pictures to movie"):
            video.write( cv2.imread(image))
        cv2.destroyAllWindows()
        video.release()
        if cleanPictures:
            for image in pictures:
                os.remove(image)

