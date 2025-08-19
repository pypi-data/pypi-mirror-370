from loguru import logger


def prestartup_patch():
    def empty_download(*args, **kwargs):
        logger.warning(f"Blocked download {args}")
        return

    import torch.hub

    torch.hub.download_url_to_file = empty_download

    import huggingface_hub

    huggingface_hub.hf_hub_download = empty_download

    if not torch.cuda.is_available():
        logger.warning("CUDA is NOT available")
        torch.cuda.current_device = lambda: 0
        torch.cuda.device_count = lambda: 1
        torch.cuda.get_device_name = lambda x=0: "Fake CUDA Device"
