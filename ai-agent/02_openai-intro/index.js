import { OpenAI } from "openai";
import 'dotenv/config';

const client = new OpenAI({
    apiKey: process.env.OPENAI_API_KEY,
});

const response = await client.chat.completions.create({
    model: "gpt-5-nano",
    messages: [{ role: "user", content: "Hello, how are you?" }],
});

console.log(response.choices[0].message.content);
