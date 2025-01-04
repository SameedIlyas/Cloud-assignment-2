import { Button } from "@/components/ui/button";
import type { FunctionComponent } from "../common/types";
import { Input } from "@/components/ui/input";
import Typewriter from "typewriter-effect";
import { useState } from "react";
import axios from "axios";

export const Home = (): FunctionComponent => {
	const [isTyping, setIsTyping] = useState(false);
	const [description, setDescription] = useState("");
	const [imageUrl, setImageUrl] = useState<string | null>(null);
	const [isLoading, setIsLoading] = useState(false);

	// const handleGenerateImage = async () => {
	// 	if (!description.trim()) {
	// 		alert("Please enter a description.");
	// 		return;
	// 	}

	// 	setIsLoading(true);
	// 	try {
	// 		const response = await axios.post("https://generation-service-706877421519.us-central1.run.app/generate-image", {
	// 			description,
	// 		});
	// 		setImageUrl(response.data.imageUrl); // Assuming server returns { imageUrl: '...' }
	// 	} catch (error) {
	// 		console.error("Error generating image:", error);
	// 		alert("Failed to generate image. Please try again.");
	// 	} finally {
	// 		setIsLoading(false);
	// 	}
	// };

	const handleGenerateImage = async () => {
		if (!description.trim()) {
			alert("Please enter a description.");
			return;
		}
	
		setIsLoading(true);
		try {
			const response = await axios.post(
				"https://generation-service-706877421519.us-central1.run.app/generate-image",
				{
					prompt: description, // Use "prompt" as in the curl request
				},
				{
					headers: {
						"Content-Type": "application/json", // Ensure correct content type
					},
				}
			);
			setImageUrl(response.data.image_url); // Assuming server returns { imageUrl: '...' }
		} catch (error) {
			console.error("Error generating image:", error);
			alert("Failed to generate image. Please try again.");
		} finally {
			setIsLoading(false);
		}
	};

	return (
		<div className="h-screen flex flex-col gap-2 bg-[#1d2023]">
			<div className="flex flex-row justify-between items-center px-10 bg-[#292c31] text-white py-10">
				<div className="text-3xl font-bold">P I X I</div>
				<div className="text-2xl font-bold">Unleash the art within your mind</div>
			</div>
			<div className="rounded-lg border-1 border-white flex flex-col bg-[#292c31] pt-14 pb-20 m-14 px-10">
				<div className="flex flex-col gap-2">
					<p className="text-2xl text-white font-bold">AI Image Generator</p>
					<p className="text-base text-white">
						Generate an image using Generative AI by describing what you want to see, all images are published publicly by default.
					</p>
				</div>
				<div className="flex flex-row justify-center gap-4 mt-10">
					<div className="relative w-full">
						{/* Typewriter effect, hidden while typing */}
						{!isTyping && (
							<div className="absolute top-2.5 left-4 text-gray-400 pointer-events-none">
								<Typewriter
									options={{
										strings: [
											"Describe your image here...",
											"e.g., A futuristic city at sunset",
											"A serene mountain landscape",
										],
										autoStart: true,
										loop: true,
									}}
								/>
							</div>
						)}
						{/* Input */}
						<Input
							type="text"
							className="w-full"
							id="description"
							placeholder=""
							value={description}
							onChange={(e) => setDescription(e.target.value)}
							onFocus={() => setIsTyping(true)}
							onBlur={(e) => {
								if (!e.target.value) setIsTyping(false);
							}}
						/>
					</div>
				</div>
				<Button
					className="ml-auto max-w-28 items-end bg-[#00a3da] mt-4"
					onClick={handleGenerateImage}
					disabled={isLoading}
				>
					{isLoading ? "Generating..." : "Generate"}
				</Button>
				{imageUrl && (
					<div className="mt-10 text-center">
						<p className="text-white text-lg mb-4">Generated Image:</p>
						<img src={imageUrl} alt="Generated" className="max-w-full mx-auto rounded-lg" />
					</div>
				)}
			</div>
		</div>
	);
};
