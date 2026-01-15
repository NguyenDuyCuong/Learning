import { getLlama, LlamaChatSession } from "node-llama-cpp";
import { fileURLToPath } from "url";
import { dirname } from "path";
import path from "path";

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

const llama = await getLlama();
const model = await llama.loadModel({
    modelPath: path.join(
        __dirname,
        "../",
        "models",
        "hf_Qwen_Qwen3-1.7B.Q8_0.gguf")
});
const context = await model.createContext();
const session = new LlamaChatSession({
    contextSequence: context.getSequence()
});
const prompt = "Hello, how are you?";
const a1 = await session.prompt(prompt);
console.log("AI: " + a1);

await session.dispose();
await context.dispose();
await model.dispose();
await llama.dispose();
