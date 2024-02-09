from arguments import InitializationArguments

from transformers import AutoConfig, AutoModelForCausalLM, GPT2Tokenizer, HfArgumentParser


if __name__ == '__main__':
    # Configuration
    parser = HfArgumentParser(InitializationArguments)
    args = parser.parse_args()

    # Load default GPT2 tokenizer from huggingface
    tokenizer = GPT2Tokenizer.from_pretrained("gpt2")

    # Config: "scale_attn_by_layer_idx" and "reorder_and_upcast_attn" are Mistral stability tweaks
    config_kwargs = {
        "vocab_size": len(tokenizer),
        "scale_attn_by_inverse_layer_idx": True,
        "reorder_and_upcast_attn": True,
    }

    # Load model config (GPT-2 small in this case)
    config = AutoConfig.from_pretrained(args.config_name, **config_kwargs)

    # Initialize new model with config
    model = AutoModelForCausalLM.from_config(config)

    # Save model to the hub
    model.save_pretrained(args.model_name, push_to_hub=args.push_to_hub)