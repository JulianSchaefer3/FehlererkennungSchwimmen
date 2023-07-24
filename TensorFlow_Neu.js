// 1. Install dependencies DONE
// 2. Import dependencies DONE
// 3. Setup webcam and canvas DONE
// 4. Define references to those DONE
// 5. Load posenet DONE
// 6. Detect function DONE
// 7. Drawing utilities from tensorflow DONE
// 8. Draw functions DONE

import React, { useRef } from "react";

import * as tf from '@tensorflow/tfjs-core';
import videoFile from './video.MP4'

import * as posenet from "@tensorflow-models/posenet";
import * as poseDetection from "@tensorflow-models/pose-detection"
import Webcam from "react-webcam";
import { drawKeypoints, drawSkeleton } from "./utilities";

// Register WebGL backend.
import '@tensorflow/tfjs-backend-webgl';

function TensorFlow_Neu() {
    const webcamRef = useRef(null);
    const videoRef = useRef(null);
    const canvasRef = useRef(null);

    //  Load posenet
    const runPosenet = async () => {
        const net = await posenet.load({
            inputResolution: { width: 640, height: 480 },
            scale: 0.8,
        });
        //
        await tf.ready()
        setInterval(() => {
            detect(net);
        }, 100);
    };

    const runPoseDetec = async () =>{
        const model = poseDetection.SupportedModels.BlazePose;
        const detectorConfig = {
            runtime: 'tfjs',
            enableSmoothing: true,
            modelType: 'full'
        };
        const detector = await poseDetection.createDetector(model, detectorConfig);
        setInterval(() => {
            detect(detector);
        }, 100);
    }

    const detect = async (net) => {


            // Get Video Properties
            const video = videoRef.current;
            const videoWidth = videoRef.current.videoWidth;
            const videoHeight = videoRef.current.videoHeight;

            // Set video width
            videoRef.current.width = videoWidth;
            videoRef.current.height = videoHeight;

            // Make Detections
            const pose = await net.estimateSinglePose(video);
            console.log(pose);

            drawCanvas(pose, video, videoWidth, videoHeight, canvasRef);

    };

    const drawCanvas = (pose, video, videoWidth, videoHeight, canvas) => {
        const ctx = canvas.current.getContext("2d");
        canvas.current.width = videoWidth;
        canvas.current.height = videoHeight;

        drawKeypoints(pose["keypoints"], 0.6, ctx);
        drawSkeleton(pose["keypoints"], 0.7, ctx);
    };
    //runPoseDetec();
    runPosenet();

    return (
        <div className="App">
            <header className="App-header">
                <video
                    ref={videoRef}
                    src = {videoFile}
                    autoPlay={true}
                    style={{
                        position: "absolute",
                        marginLeft: "auto",
                        marginRight: "auto",
                        left: 0,
                        right: 0,
                        textAlign: "center",
                        zindex: 9,
                        width: 640,
                        height: 480,
                    }}
                    controls
                    loop
                />

                <canvas
                    ref={canvasRef}
                    style={{
                        position: "absolute",
                        marginLeft: "auto",
                        marginRight: "auto",
                        left: 0,
                        right: 0,
                        textAlign: "center",
                        zindex: 9,
                        width: 640,
                        height: 480,
                    }}
                />
            </header>
        </div>
    );
}

export default TensorFlow_Neu;
