from aiohttp import (
    ClientResponseError,
    ClientSession,
    ClientTimeout
)
from aiohttp_socks import ProxyConnector
from eth_account import Account
from web3 import Web3
from colorama import *
from datetime import datetime
import asyncio, random, json, time, os, pytz

wib = pytz.timezone('Asia/Jakarta')

class XosTestnet:
    def __init__(self) -> None:
        self.RPC_URL = "https://testnet-rpc.x.ink/"
        self.WXOS_CONTRACT_ADDRESS = "0x0AAB67cf6F2e99847b9A95DeC950B250D648c1BB"
        self.BNB_CONTRACT_ADDRESS = "0x83DFbE02dc1B1Db11bc13a8Fc7fd011E2dBbd7c0"
        self.BONK_CONTRACT_ADDRESS = "0x00309602f7977D45322279c4dD5cf61D16FD061B"
        self.JUP_CONTRACT_ADDRESS = "0x26b597804318824a2E88Cd717376f025E6bb2219"
        self.PENGU_CONTRACT_ADDRESS = "0x9573577927d3AbECDa9C69F5E8C50bc88b1e26EE"
        self.RAY_CONTRACT_ADDRESS = "0x4A79C7Fdb6d448b3f8F643010F4CdE8b2363EFD6"
        self.SOL_CONTRACT_ADDRESS = "0x0c8a3D1fE7E40a39D3331D5Fa4B9fee1EcA1926A"
        self.TRUMP_CONTRACT_ADDRESS = "0xC09a5026d9244d482Fb913609Aeb7347B7F12800"
        self.TST_CONTRACT_ADDRESS = "0xD1194D2D06EDFBD815574383aeD6A9D76Cd568dA"
        self.USDC_CONTRACT_ADDRESS = "0xb2C1C007421f0Eb5f4B3b3F38723C309Bb208d7d"
        self.USDT_CONTRACT_ADDRESS = "0x2CCDB83a043A32898496c1030880Eb2cB977CAbc"
        self.WIF_CONTRACT_ADDRESS = "0x9c6eEc453821d12B8dfea20b6FbdDB47f7bc500d"
        self.SWAP_ROUTER_ADDRESS = "0xdc7D6b58c89A554b3FDC4B5B10De9b4DbF39FB40"
        self.ERC20_CONTRACT_ABI = json.loads('''[
            {"type":"function","name":"balanceOf","stateMutability":"view","inputs":[{"name":"address","type":"address"}],"outputs":[{"name":"","type":"uint256"}]},
            {"type":"function","name":"allowance","stateMutability":"view","inputs":[{"name":"owner","type":"address"},{"name":"spender","type":"address"}],"outputs":[{"name":"","type":"uint256"}]},
            {"type":"function","name":"approve","stateMutability":"nonpayable","inputs":[{"name":"spender","type":"address"},{"name":"amount","type":"uint256"}],"outputs":[{"name":"","type":"bool"}]},
            {"type":"function","name":"decimals","stateMutability":"view","inputs":[],"outputs":[{"name":"","type":"uint8"}]},
            {"type":"function","name":"deposit","stateMutability":"payable","inputs":[],"outputs":[]},
            {"type":"function","name":"withdraw","stateMutability":"nonpayable","inputs":[{"name":"wad","type":"uint256"}],"outputs":[]}
        ]''')
        self.SWAP_CONTRACT_ABI = [
            {
                "inputs": [
                    {
                        "components": [
                            { "internalType": "address", "name": "tokenIn", "type": "address" },
                            { "internalType": "address", "name": "tokenOut", "type": "address" },
                            { "internalType": "uint24", "name": "fee", "type": "uint24" },
                            { "internalType": "address", "name": "recipient", "type": "address" },
                            { "internalType": "uint256", "name": "amountIn", "type": "uint256" },
                            { "internalType": "uint256", "name": "amountOutMinimum", "type": "uint256" },
                            { "internalType": "uint160", "name": "sqrtPriceLimitX96", "type": "uint160" },
                        ],
                        "internalType": "struct IV3SwapRouter.ExactInputSingleParams",
                        "name": "params",
                        "type": "tuple",
                    },
                ],
                "name": "exactInputSingle",
                "outputs": [
                    { "internalType": "uint256", "name": "amountOut", "type": "uint256" }
                ],
                "stateMutability": "payable",
                "type": "function",
            },
            {
                "inputs": [
                    {
                        "components": [
                            { "internalType": "bytes", "name": "path", "type": "bytes" },
                            { "internalType": "address", "name": "recipient", "type": "address" },
                            { "internalType": "uint256", "name": "amountIn", "type": "uint256" },
                            { "internalType": "uint256", "name": "amountOutMinimum", "type": "uint256" },
                        ],
                        "internalType": "struct IV3SwapRouter.ExactInputParams",
                        "name": "params",
                        "type": "tuple",
                    },
                ],
                "name": "exactInput",
                "outputs": [
                    { "internalType": "uint256", "name": "amountOut", "type": "uint256" }
                ],
                "stateMutability": "payable",
                "type": "function",
            },
            {
                "inputs": [
                    { "internalType": "uint256", "name": "deadline", "type": "uint256" },
                    { "internalType": "bytes[]", "name": "data", "type": "bytes[]" } 
                ], 
                "name": "multicall", 
                "outputs": [ 
                    { "internalType": "bytes[]", "name": "", "type": "bytes[]" } 
                ],
                "stateMutability": "payable",
                "type": "function"
            },
        ]
        self.proxies = []
        self.proxy_index = 0
        self.account_proxies = {}

    def clear_terminal(self):
        os.system('cls' if os.name == 'nt' else 'clear')

    def log(self, message):
        print(
            f"{Fore.CYAN + Style.BRIGHT}[ {datetime.now().astimezone(wib).strftime('%x %X %Z')} ]{Style.RESET_ALL}"
            f"{Fore.WHITE + Style.BRIGHT} | {Style.RESET_ALL}{message}",
            flush=True
        )

    def welcome(self):
        print(
            f"""
        {Fore.GREEN + Style.BRIGHT}XOS Testnet{Fore.BLUE + Style.BRIGHT} Auto BOT
            """
            f"""
        {Fore.GREEN + Style.BRIGHT}Rey? {Fore.YELLOW + Style.BRIGHT}<INI WATERMARK>
            """
        )

    def format_seconds(self, seconds):
        hours, remainder = divmod(seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        return f"{int(hours):02}:{int(minutes):02}:{int(seconds):02}"
    
    async def load_proxies(self, use_proxy_choice: int):
        filename = "proxy.txt"
        try:
            if use_proxy_choice == 1:
                async with ClientSession(timeout=ClientTimeout(total=30)) as session:
                    async with session.get("https://raw.githubusercontent.com/monosans/proxy-list/main/proxies/all.txt") as response:
                        response.raise_for_status()
                        content = await response.text()
                        with open(filename, 'w') as f:
                            f.write(content)
                        self.proxies = content.splitlines()
            else:
                if not os.path.exists(filename):
                    self.log(f"{Fore.RED + Style.BRIGHT}File {filename} Not Found.{Style.RESET_ALL}")
                    return
                with open(filename, 'r') as f:
                    self.proxies = f.read().splitlines()
            
            if not self.proxies:
                self.log(f"{Fore.RED + Style.BRIGHT}No Proxies Found.{Style.RESET_ALL}")
                return

            self.log(
                f"{Fore.GREEN + Style.BRIGHT}Proxies Total  : {Style.RESET_ALL}"
                f"{Fore.WHITE + Style.BRIGHT}{len(self.proxies)}{Style.RESET_ALL}"
            )
        
        except Exception as e:
            self.log(f"{Fore.RED + Style.BRIGHT}Failed To Load Proxies: {e}{Style.RESET_ALL}")
            self.proxies = []

    def check_proxy_schemes(self, proxies):
        schemes = ["http://", "https://", "socks4://", "socks5://"]
        if any(proxies.startswith(scheme) for scheme in schemes):
            return proxies
        return f"http://{proxies}"

    def get_next_proxy_for_account(self, token):
        if token not in self.account_proxies:
            if not self.proxies:
                return None
            proxy = self.check_proxy_schemes(self.proxies[self.proxy_index])
            self.account_proxies[token] = proxy
            self.proxy_index = (self.proxy_index + 1) % len(self.proxies)
        return self.account_proxies[token]

    def rotate_proxy_for_account(self, token):
        if not self.proxies:
            return None
        proxy = self.check_proxy_schemes(self.proxies[self.proxy_index])
        self.account_proxies[token] = proxy
        self.proxy_index = (self.proxy_index + 1) % len(self.proxies)
        return proxy
    
    def generate_address(self, account: str):
        try:
            account = Account.from_key(account)
            address = account.address
            
            return address
        except Exception as e:
            raise Exception(f"Generate Addres From Private Key Failed: {str(e)}")
        
    def generate_swap_option(self):
        swap_option = random.choice([
            "WXOStoBNB", "WXOStoBONK", "WXOStoJUP", "WXOStoPENGU", "WXOStoRAY", 
            "WXOStoSOL", "WXOStoTRUMP", "WXOStoTST", "WXOStoUSDC", "WXOStoUSDT", 
            "WXOStoWIF", "BNBtoWXOS",  "BONKtoWXOS", "JUPtoWXOS", "PENGUtoWXOS", 
            "RAYtoWXOS", "SOLtoWXOS", "TRUMPtoWXOS", "TSTtoWXOS", "USDCtoWXOS",
            "USDTtoWXOS", "WIFtoWXOS",
        ])

        from_contract_address = (
            self.BNB_CONTRACT_ADDRESS if swap_option == "BNBtoWXOS" else
            self.BONK_CONTRACT_ADDRESS if swap_option == "BONKtoWXOS" else
            self.JUP_CONTRACT_ADDRESS if swap_option == "JUPtoWXOS" else
            self.PENGU_CONTRACT_ADDRESS if swap_option == "PENGUtoWXOS" else
            self.RAY_CONTRACT_ADDRESS if swap_option == "RAYtoWXOS" else
            self.SOL_CONTRACT_ADDRESS if swap_option == "SOLtoWXOS" else
            self.TRUMP_CONTRACT_ADDRESS if swap_option == "TRUMPtoWXOS" else
            self.TST_CONTRACT_ADDRESS if swap_option == "TSTtoWXOS" else
            self.USDC_CONTRACT_ADDRESS if swap_option == "USDCtoWXOS" else
            self.USDT_CONTRACT_ADDRESS if swap_option == "USDTtoWXOS" else
            self.WIF_CONTRACT_ADDRESS if swap_option == "WIFtoWXOS" else
            self.WXOS_CONTRACT_ADDRESS
        )

        to_contract_address = (
            self.BNB_CONTRACT_ADDRESS if swap_option == "WXOStoBNB" else
            self.BONK_CONTRACT_ADDRESS if swap_option == "WXOStoBONK" else
            self.JUP_CONTRACT_ADDRESS if swap_option == "WXOStoJUP" else
            self.PENGU_CONTRACT_ADDRESS if swap_option == "WXOStoPENGU" else
            self.RAY_CONTRACT_ADDRESS if swap_option == "WXOStoRAY" else
            self.SOL_CONTRACT_ADDRESS if swap_option == "WXOStoSOL" else
            self.TRUMP_CONTRACT_ADDRESS if swap_option == "WXOStoTRUMP" else
            self.TST_CONTRACT_ADDRESS if swap_option == "WXOStoTST" else
            self.USDC_CONTRACT_ADDRESS if swap_option == "WXOStoUSDC" else
            self.USDT_CONTRACT_ADDRESS if swap_option == "WXOStoUSDT" else
            self.WIF_CONTRACT_ADDRESS if swap_option == "WXOStoWIF" else
            self.WXOS_CONTRACT_ADDRESS
        )

        from_token = (
            "BNB" if swap_option == "BNBtoWXOS" else
            "BONK" if swap_option == "BONKtoWXOS" else
            "JUP" if swap_option == "JUPtoWXOS" else
            "PENGU" if swap_option == "PENGUtoWXOS" else
            "RAY" if swap_option == "RAYtoWXOS" else
            "SOL" if swap_option == "SOLtoWXOS" else
            "TRUMP" if swap_option == "TRUMPtoWXOS" else
            "TST" if swap_option == "TSTtoWXOS" else
            "USDC" if swap_option == "USDCtoWXOS" else
            "USDT" if swap_option == "USDTtoWXOS" else
            "WIF" if swap_option == "WIFtoWXOS" else
            "WXOS"
        )

        to_token = (
            "BNB" if swap_option == "WXOStoBNB" else
            "BONK" if swap_option == "WXOStoBONK" else
            "JUP" if swap_option == "WXOStoJUP" else
            "PENGU" if swap_option == "WXOStoPENGU" else
            "RAY" if swap_option == "WXOStoRAY" else
            "SOL" if swap_option == "WXOStoSOL" else
            "TRUMP" if swap_option == "WXOStoTRUMP" else
            "TST" if swap_option == "WXOStoTST" else
            "USDC" if swap_option == "WXOStoUSDC" else
            "USDT" if swap_option == "WXOStoUSDT" else
            "WIF" if swap_option == "WXOStoWIF" else
            "WXOS"
        )

        return from_contract_address, to_contract_address, from_token, to_token
        
    async def get_web3_with_check(self, retries=3, timeout=60):
        for i in range(retries):
            try:
                web3 = Web3(Web3.HTTPProvider(self.RPC_URL, request_kwargs={"timeout": timeout}))
                web3.eth.get_block_number()
                return web3
            except Exception as e:
                await asyncio.sleep(3)
        raise Exception(f"Failed to Connect to RPC: {str(e)}")
        
    async def get_token_balance(self, address: str, contract_address: str):
        try:
            web3 = await self.get_web3_with_check()

            if contract_address == "PHRS":
                balance = web3.eth.get_balance(address)
                decimals = 18
            else:
                token_contract = web3.eth.contract(address=web3.to_checksum_address(contract_address), abi=self.ERC20_CONTRACT_ABI)
                decimals = token_contract.functions.decimals().call({"from": address})
                balance = token_contract.functions.balanceOf(address).call()

            token_balance = balance / (10 ** decimals)

            return token_balance
        except Exception as e:
            self.log(
                f"{Fore.CYAN+Style.BRIGHT}     Message :{Style.RESET_ALL}"
                f"{Fore.RED+Style.BRIGHT} {str(e)} {Style.RESET_ALL}"
            )
            return None

    async def perform_wrap(self, account: str, address: str, amount: float):
        try:
            web3 = await self.get_web3_with_check()
            contract_address = web3.to_checksum_address(self.WXOS_CONTRACT_ADDRESS)
            token_contract = web3.eth.contract(address=contract_address, abi=self.ERC20_CONTRACT_ABI)

            amount_to_wei = web3.to_wei(amount, "ether")
            wrap_data = token_contract.functions.deposit()
            estimated_gas = wrap_data.estimate_gas({"from": address, "value": amount_to_wei})

            max_priority_fee = web3.to_wei(78.75, "gwei")
            max_fee = max_priority_fee

            wrap_tx = wrap_data.build_transaction({
                "from": address,
                "value": amount_to_wei,
                "gas": int(estimated_gas * 1.2),
                "maxFeePerGas": int(max_fee),
                "maxPriorityFeePerGas": int(max_priority_fee),
                "nonce": web3.eth.get_transaction_count(address, "pending"),
                "chainId": web3.eth.chain_id,
            })

            signed_tx = web3.eth.account.sign_transaction(wrap_tx, account)
            raw_tx = web3.eth.send_raw_transaction(signed_tx.raw_transaction)
            tx_hash = web3.to_hex(raw_tx)
            receipt = await asyncio.to_thread(web3.eth.wait_for_transaction_receipt, tx_hash, timeout=300)
            block_number = receipt.blockNumber

            return tx_hash, block_number
        except Exception as e:
            self.log(
                f"{Fore.CYAN+Style.BRIGHT}     Message :{Style.RESET_ALL}"
                f"{Fore.RED+Style.BRIGHT} {str(e)} {Style.RESET_ALL}"
            )
            return None, None
        
    async def perform_unwrap(self, account: str, address: str, amount: float):
        try:
            web3 = await self.get_web3_with_check()
            contract_address = web3.to_checksum_address(self.WXOS_CONTRACT_ADDRESS)
            token_contract = web3.eth.contract(address=contract_address, abi=self.ERC20_CONTRACT_ABI)

            amount_to_wei = web3.to_wei(amount, "ether")
            unwrap_data = token_contract.functions.withdraw(amount_to_wei)
            estimated_gas = unwrap_data.estimate_gas({"from": address})

            max_priority_fee = web3.to_wei(78.75, "gwei")
            max_fee = max_priority_fee

            unwrap_tx = unwrap_data.build_transaction({
                "from": address,
                "gas": int(estimated_gas * 1.2),
                "maxFeePerGas": int(max_fee),
                "maxPriorityFeePerGas": int(max_priority_fee),
                "nonce": web3.eth.get_transaction_count(address, "pending"),
                "chainId": web3.eth.chain_id,
            })

            signed_tx = web3.eth.account.sign_transaction(unwrap_tx, account)
            raw_tx = web3.eth.send_raw_transaction(signed_tx.raw_transaction)
            tx_hash = web3.to_hex(raw_tx)
            receipt = await asyncio.to_thread(web3.eth.wait_for_transaction_receipt, tx_hash, timeout=300)
            block_number = receipt.blockNumber

            return tx_hash, block_number
        except Exception as e:
            self.log(
                f"{Fore.CYAN+Style.BRIGHT}     Message :{Style.RESET_ALL}"
                f"{Fore.RED+Style.BRIGHT} {str(e)} {Style.RESET_ALL}"
            )
            return None, None
        
    async def approving_token(self, account: str, address: str, spender_address: str, contract_address: str, amount: float):
        try:
            web3 = await self.get_web3_with_check()
            spender = web3.to_checksum_address(spender_address)
            token_contract = web3.eth.contract(address=web3.to_checksum_address(contract_address), abi=self.ERC20_CONTRACT_ABI)

            amount_to_wei = web3.to_wei(amount, "ether")

            allowance = token_contract.functions.allowance(address, spender).call()
            if allowance < amount_to_wei:
                approve_data = token_contract.functions.approve(spender, 2**256 - 1)
                estimated_gas = approve_data.estimate_gas({"from": address})

                max_priority_fee = web3.to_wei(78.75, "gwei")
                max_fee = max_priority_fee

                approve_tx = approve_data.build_transaction({
                    "from": address,
                    "gas": int(estimated_gas * 1.2),
                    "maxFeePerGas": int(max_fee),
                    "maxPriorityFeePerGas": int(max_priority_fee),
                    "nonce": web3.eth.get_transaction_count(address, "pending"),
                    "chainId": web3.eth.chain_id,
                })

                signed_tx = web3.eth.account.sign_transaction(approve_tx, account)
                raw_tx = web3.eth.send_raw_transaction(signed_tx.raw_transaction)
                tx_hash = web3.to_hex(raw_tx)
                receipt = await asyncio.to_thread(web3.eth.wait_for_transaction_receipt, tx_hash, timeout=300)
                block_number = receipt.blockNumber

            return True
        except Exception as e:
            raise Exception(f"Approving Token Contract Failed: {str(e)}")
        
    async def perform_swap(self, account: str, address: str, from_contract_address: str, to_contract_address: str, swap_amount: float):
        try:
            web3 = await self.get_web3_with_check()
            await self.approving_token(account, address, self.SWAP_ROUTER_ADDRESS, from_contract_address, swap_amount)

            token_contract = web3.eth.contract(address=web3.to_checksum_address(self.SWAP_ROUTER_ADDRESS), abi=self.SWAP_CONTRACT_ABI)

            params = {
                "tokenIn": web3.to_checksum_address(from_contract_address),
                "tokenOut": web3.to_checksum_address(to_contract_address),
                "fee": 500,
                "recipient": address,
                "amountIn": web3.to_wei(swap_amount, "ether"),
                "amountOutMinimum": 0,
                "sqrtPriceLimitX96": 0,
            }

            multicall = token_contract.functions.exactInputSingle(params).build_transaction({
                "from": address,
                "nonce": web3.eth.get_transaction_count(address, "pending")
            })
            
            deadline = int(time.time()) + 300

            swap_data = token_contract.functions.multicall(deadline, [multicall["data"]])

            estimated_gas = swap_data.estimate_gas({"from": address})
            max_priority_fee = web3.to_wei(78.75, "gwei")
            max_fee = max_priority_fee

            swap_tx = swap_data.build_transaction({
                "from": address,
                "gas": int(estimated_gas * 1.2),
                "maxFeePerGas": int(max_fee),
                "maxPriorityFeePerGas": int(max_priority_fee),
                "nonce": web3.eth.get_transaction_count(address, "pending"),
                "chainId": web3.eth.chain_id,
            })

            signed_tx = web3.eth.account.sign_transaction(swap_tx, account)
            raw_tx = web3.eth.send_raw_transaction(signed_tx.raw_transaction)
            tx_hash = web3.to_hex(raw_tx)
            receipt = await asyncio.to_thread(web3.eth.wait_for_transaction_receipt, tx_hash, timeout=300)
            block_number = receipt.blockNumber

            return tx_hash, block_number
        except Exception as e:
            self.log(
                f"{Fore.CYAN+Style.BRIGHT}     Message :{Style.RESET_ALL}"
                f"{Fore.RED+Style.BRIGHT} {str(e)} {Style.RESET_ALL}"
            )
            return None, None
    
    def mask_account(self, account):
        mask_account = account[:6] + '*' * 6 + account[-6:]
        return mask_account 
    
    async def print_timer(self, min_delay: int, max_delay: int):
        for remaining in range(random.randint(min_delay, max_delay), 0, -1):
            print(
                f"{Fore.CYAN + Style.BRIGHT}[ {datetime.now().astimezone(wib).strftime('%x %X %Z')} ]{Style.RESET_ALL}"
                f"{Fore.WHITE + Style.BRIGHT} | {Style.RESET_ALL}"
                f"{Fore.BLUE + Style.BRIGHT}Wait For{Style.RESET_ALL}"
                f"{Fore.WHITE + Style.BRIGHT} {remaining} {Style.RESET_ALL}"
                f"{Fore.BLUE + Style.BRIGHT}Seconds For Next Tx...{Style.RESET_ALL}",
                end="\r",
                flush=True
            )
            await asyncio.sleep(1)

    def print_question(self):
        wrap_option = None
        wrap_amount = 0
        swap_count = 0
        min_swap_amount = 0
        max_swap_amount = 0
        rotate = False

        while True:
            try:
                print(f"{Fore.GREEN + Style.BRIGHT}Select Option:{Style.RESET_ALL}")
                print(f"{Fore.WHITE + Style.BRIGHT}1. Wrap - Unwrap{Style.RESET_ALL}")
                print(f"{Fore.WHITE + Style.BRIGHT}2. Swap{Style.RESET_ALL}")
                print(f"{Fore.WHITE + Style.BRIGHT}3. Run All Features{Style.RESET_ALL}")
                option = int(input(f"{Fore.BLUE + Style.BRIGHT}Choose [1/2/3] -> {Style.RESET_ALL}").strip())

                if option in [1, 2, 3]:
                    option_type = (
                        "Wrap - Unwrap" if option == 1 else 
                        "Swap" if option == 2 else 
                        "Run All Features"
                    )
                    print(f"{Fore.GREEN + Style.BRIGHT}{option_type} Selected.{Style.RESET_ALL}")
                    break
                else:
                    print(f"{Fore.RED + Style.BRIGHT}Please enter either 1, 2 or 3.{Style.RESET_ALL}")
            except ValueError:
                print(f"{Fore.RED + Style.BRIGHT}Invalid input. Enter a number (1, 2 or 3).{Style.RESET_ALL}")

        if option == 1:
            while True:
                try:
                    print(f"{Fore.GREEN + Style.BRIGHT}Select Option:{Style.RESET_ALL}")
                    print(f"{Fore.WHITE + Style.BRIGHT}1. Wrap XOS to WXOS{Style.RESET_ALL}")
                    print(f"{Fore.WHITE + Style.BRIGHT}2. Unwrap WXOS to XOS{Style.RESET_ALL}")
                    wrap_option = int(input(f"{Fore.BLUE + Style.BRIGHT}Choose [1/2] -> {Style.RESET_ALL}").strip())

                    if wrap_option in [1, 2]:
                        wrap_type = (
                            "Wrap XOS to WXOS" if wrap_option == 1 else 
                            "Unwrap WXOS to XOS"
                        )
                        print(f"{Fore.GREEN + Style.BRIGHT}{wrap_type} Selected.{Style.RESET_ALL}")
                        break
                    else:
                        print(f"{Fore.RED + Style.BRIGHT}Please enter either 1 or 2.{Style.RESET_ALL}")
                except ValueError:
                    print(f"{Fore.RED + Style.BRIGHT}Invalid input. Enter a number (1 or 2).{Style.RESET_ALL}")

            while True:
                try:
                    wrap_amount = float(input(f"{Fore.YELLOW + Style.BRIGHT}Enter Amount [1 or 0.01 or 0.001, etc in decimals] -> {Style.RESET_ALL}").strip())
                    if wrap_amount > 0:
                        break
                    else:
                        print(f"{Fore.RED + Style.BRIGHT}Amount must be greater than 0.{Style.RESET_ALL}")
                except ValueError:
                    print(f"{Fore.RED + Style.BRIGHT}Invalid input. Enter a float or decimal number.{Style.RESET_ALL}")

        elif option == 2:
            while True:
                try:
                    swap_count = int(input(f"{Fore.YELLOW + Style.BRIGHT}How Many Times Do You Want To Make a Swap? -> {Style.RESET_ALL}").strip())
                    if swap_count > 0:
                        break
                    else:
                        print(f"{Fore.RED + Style.BRIGHT}Please enter positive number.{Style.RESET_ALL}")
                except ValueError:
                    print(f"{Fore.RED + Style.BRIGHT}Invalid input. Enter a number.{Style.RESET_ALL}")

            while True:
                try:
                    min_swap_amount = float(input(f"{Fore.YELLOW + Style.BRIGHT}Min Swap Amount? [1 or 0.01 or 0.001, etc in decimals]-> {Style.RESET_ALL}").strip())
                    if min_swap_amount > 0:
                        break
                    else:
                        print(f"{Fore.RED + Style.BRIGHT}Amount must be greater than 0.{Style.RESET_ALL}")
                except ValueError:
                    print(f"{Fore.RED + Style.BRIGHT}Invalid input. Enter a number.{Style.RESET_ALL}")

            while True:
                try:
                    max_swap_amount = float(input(f"{Fore.YELLOW + Style.BRIGHT}Max Swap Amount? [1 or 0.01 or 0.001, etc in decimals]-> {Style.RESET_ALL}").strip())
                    if max_swap_amount > 0 and max_swap_amount >= min_swap_amount:
                        break
                    else:
                        print(f"{Fore.RED + Style.BRIGHT}Amount must be greater than 0 and >= Min Swap Amount.{Style.RESET_ALL}")
                except ValueError:
                    print(f"{Fore.RED + Style.BRIGHT}Invalid input. Enter a number.{Style.RESET_ALL}")

        elif option == 3:
            while True:
                try:
                    print(f"{Fore.GREEN + Style.BRIGHT}Select Option:{Style.RESET_ALL}")
                    print(f"{Fore.WHITE + Style.BRIGHT}1. Wrap XOS to WXOS{Style.RESET_ALL}")
                    print(f"{Fore.WHITE + Style.BRIGHT}2. Unwrap WXOS to XOS{Style.RESET_ALL}")
                    wrap_option = int(input(f"{Fore.BLUE + Style.BRIGHT}Choose [1/2] -> {Style.RESET_ALL}").strip())

                    if wrap_option in [1, 2]:
                        wrap_type = (
                            "Wrap XOS to WXOS" if wrap_option == 1 else 
                            "Unwrap WXOS to XOS"
                        )
                        print(f"{Fore.GREEN + Style.BRIGHT}{wrap_type} Selected.{Style.RESET_ALL}")
                        break
                    else:
                        print(f"{Fore.RED + Style.BRIGHT}Please enter either 1 or 2.{Style.RESET_ALL}")
                except ValueError:
                    print(f"{Fore.RED + Style.BRIGHT}Invalid input. Enter a number (1 or 2).{Style.RESET_ALL}")

            while True:
                try:
                    min_swap_amount = float(input(f"{Fore.YELLOW + Style.BRIGHT}Min Swap Amount? [1 or 0.01 or 0.001, etc in decimals]-> {Style.RESET_ALL}").strip())
                    if min_swap_amount > 0:
                        break
                    else:
                        print(f"{Fore.RED + Style.BRIGHT}Amount must be greater than 0.{Style.RESET_ALL}")
                except ValueError:
                    print(f"{Fore.RED + Style.BRIGHT}Invalid input. Enter a number.{Style.RESET_ALL}")

            while True:
                try:
                    max_swap_amount = float(input(f"{Fore.YELLOW + Style.BRIGHT}Max Swap Amount? [1 or 0.01 or 0.001, etc in decimals]-> {Style.RESET_ALL}").strip())
                    if max_swap_amount > 0 and max_swap_amount >= min_swap_amount:
                        break
                    else:
                        print(f"{Fore.RED + Style.BRIGHT}Amount must be greater than 0 and >= Min Swap Amount.{Style.RESET_ALL}")
                except ValueError:
                    print(f"{Fore.RED + Style.BRIGHT}Invalid input. Enter a number.{Style.RESET_ALL}")

        while True:
            try:
                print(f"{Fore.WHITE + Style.BRIGHT}1. Run With Monosans Proxy{Style.RESET_ALL}")
                print(f"{Fore.WHITE + Style.BRIGHT}2. Run With Private Proxy{Style.RESET_ALL}")
                print(f"{Fore.WHITE + Style.BRIGHT}3. Run Without Proxy{Style.RESET_ALL}")
                choose = int(input(f"{Fore.BLUE + Style.BRIGHT}Choose [1/2/3] -> {Style.RESET_ALL}").strip())

                if choose in [1, 2, 3]:
                    proxy_type = (
                        "Run With Monosans Proxy" if choose == 1 else 
                        "Run With Private Proxy" if choose == 2 else 
                        "Run Without Proxy"
                    )
                    print(f"{Fore.GREEN + Style.BRIGHT}{proxy_type} Selected.{Style.RESET_ALL}")
                    break
                else:
                    print(f"{Fore.RED + Style.BRIGHT}Please enter either 1, 2 or 3.{Style.RESET_ALL}")
            except ValueError:
                print(f"{Fore.RED + Style.BRIGHT}Invalid input. Enter a number (1, 2 or 3).{Style.RESET_ALL}")

        if choose in [1, 2]:
            while True:
                rotate = input(f"{Fore.BLUE + Style.BRIGHT}Rotate Invalid Proxy? [y/n] -> {Style.RESET_ALL}").strip()

                if rotate in ["y", "n"]:
                    rotate = rotate == "y"
                    break
                else:
                    print(f"{Fore.RED + Style.BRIGHT}Invalid input. Enter 'y' or 'n'.{Style.RESET_ALL}")

        return option, wrap_option, wrap_amount, swap_count, min_swap_amount, max_swap_amount, choose, rotate
    
    async def check_connection(self, proxy=None):
        connector = ProxyConnector.from_url(proxy) if proxy else None
        try:
            async with ClientSession(connector=connector, timeout=ClientTimeout(total=30)) as session:
                async with session.get(url="https://dex.x.ink", headers={}) as response:
                    response.raise_for_status()
                    return True
        except (Exception, ClientResponseError) as e:
            return None
            
    async def process_check_connection(self, address: str, use_proxy: bool, rotate_proxy: bool):
        message = "Checking Connection, Wait..."
        if use_proxy:
            message = "Checking Proxy Connection, Wait..."

        print(
            f"{Fore.CYAN + Style.BRIGHT}[ {datetime.now().astimezone(wib).strftime('%x %X %Z')} ]{Style.RESET_ALL}"
            f"{Fore.WHITE + Style.BRIGHT} | {Style.RESET_ALL}"
            f"{Fore.YELLOW + Style.BRIGHT}{message}{Style.RESET_ALL}",
            end="\r",
            flush=True
        )

        proxy = self.get_next_proxy_for_account(address) if use_proxy else None

        if rotate_proxy:
            is_valid = None
            while is_valid is None:
                is_valid = await self.check_connection(proxy)
                if not is_valid:
                    self.log(
                        f"{Fore.CYAN+Style.BRIGHT}Proxy     :{Style.RESET_ALL}"
                        f"{Fore.WHITE+Style.BRIGHT} {proxy} {Style.RESET_ALL}"
                        f"{Fore.MAGENTA+Style.BRIGHT}-{Style.RESET_ALL}"
                        f"{Fore.RED+Style.BRIGHT} Not 200 OK, {Style.RESET_ALL}"
                        f"{Fore.YELLOW+Style.BRIGHT}Rotating Proxy...{Style.RESET_ALL}"
                    )
                    proxy = self.rotate_proxy_for_account(address) if use_proxy else None
                    await asyncio.sleep(5)
                    continue

                self.log(
                    f"{Fore.CYAN+Style.BRIGHT}Proxy     :{Style.RESET_ALL}"
                    f"{Fore.WHITE+Style.BRIGHT} {proxy} {Style.RESET_ALL}"
                    f"{Fore.MAGENTA+Style.BRIGHT}-{Style.RESET_ALL}"
                    f"{Fore.GREEN+Style.BRIGHT} 200 OK {Style.RESET_ALL}                  "
                )

                return True

        is_valid = await self.check_connection(proxy)
        if not is_valid:
            self.log(
                f"{Fore.CYAN+Style.BRIGHT}Proxy     :{Style.RESET_ALL}"
                f"{Fore.WHITE+Style.BRIGHT} {proxy} {Style.RESET_ALL}"
                f"{Fore.MAGENTA+Style.BRIGHT}-{Style.RESET_ALL}"
                f"{Fore.RED+Style.BRIGHT} Not 200 OK {Style.RESET_ALL}          "
            )
            return False
        
        self.log(
            f"{Fore.CYAN+Style.BRIGHT}Proxy     :{Style.RESET_ALL}"
            f"{Fore.WHITE+Style.BRIGHT} {proxy} {Style.RESET_ALL}"
            f"{Fore.MAGENTA+Style.BRIGHT}-{Style.RESET_ALL}"
            f"{Fore.GREEN+Style.BRIGHT} 200 OK {Style.RESET_ALL}                  "
        )

        return True
    
    async def process_perform_wrap(self, account: str, address: str, wrap_amount: float):
        tx_hash, block_number = await self.perform_wrap(account, address, wrap_amount)
        if tx_hash and block_number:
            explorer = f"https://testnet.xoscan.io/tx/{tx_hash}"
            self.log(
                f"{Fore.CYAN+Style.BRIGHT}     Status  :{Style.RESET_ALL}"
                f"{Fore.GREEN+Style.BRIGHT} Wrap {wrap_amount} XOS to WXOS Success {Style.RESET_ALL}"
            )
            self.log(
                f"{Fore.CYAN+Style.BRIGHT}     Block   :{Style.RESET_ALL}"
                f"{Fore.WHITE+Style.BRIGHT} {block_number} {Style.RESET_ALL}"
            )
            self.log(
                f"{Fore.CYAN+Style.BRIGHT}     Tx Hash :{Style.RESET_ALL}"
                f"{Fore.WHITE+Style.BRIGHT} {tx_hash} {Style.RESET_ALL}"
            )
            self.log(
                f"{Fore.CYAN+Style.BRIGHT}     Explorer:{Style.RESET_ALL}"
                f"{Fore.WHITE+Style.BRIGHT} {explorer} {Style.RESET_ALL}"
            )
        else:
            self.log(
                f"{Fore.CYAN+Style.BRIGHT}     Status  :{Style.RESET_ALL}"
                f"{Fore.RED+Style.BRIGHT} Perform On-Chain Failed {Style.RESET_ALL}"
            )

    async def process_perform_unwrap(self, account: str, address: str, wrap_amount: float):
        tx_hash, block_number = await self.perform_unwrap(account, address, wrap_amount)
        if tx_hash and block_number:
            explorer = f"https://testnet.xoscan.io/tx/{tx_hash}"

            self.log(
                f"{Fore.CYAN+Style.BRIGHT}     Status  :{Style.RESET_ALL}"
                f"{Fore.GREEN+Style.BRIGHT} Unwrap {wrap_amount} WXOS to XOS Success {Style.RESET_ALL}"
            )
            self.log(
                f"{Fore.CYAN+Style.BRIGHT}     Block   :{Style.RESET_ALL}"
                f"{Fore.WHITE+Style.BRIGHT} {block_number} {Style.RESET_ALL}"
            )
            self.log(
                f"{Fore.CYAN+Style.BRIGHT}     Tx Hash :{Style.RESET_ALL}"
                f"{Fore.WHITE+Style.BRIGHT} {tx_hash} {Style.RESET_ALL}"
            )
            self.log(
                f"{Fore.CYAN+Style.BRIGHT}     Explorer:{Style.RESET_ALL}"
                f"{Fore.WHITE+Style.BRIGHT} {explorer} {Style.RESET_ALL}"
            )
        else:
            self.log(
                f"{Fore.CYAN+Style.BRIGHT}     Status  :{Style.RESET_ALL}"
                f"{Fore.RED+Style.BRIGHT} Perform On-Chain Failed {Style.RESET_ALL}"
            )

    async def process_perform_swap(self, account: str, address: str, from_contract_address: str, to_contract_address: str, from_token: str, to_token: str, swap_amount: float):
        tx_hash, block_number = await self.perform_swap(account, address, from_contract_address, to_contract_address, swap_amount)
        if tx_hash and block_number:
            explorer = f"https://testnet.xoscan.io/tx/{tx_hash}"

            self.log(
                f"{Fore.CYAN+Style.BRIGHT}     Status  :{Style.RESET_ALL}"
                f"{Fore.GREEN+Style.BRIGHT} Swap {swap_amount} {from_token} to {to_token} Success {Style.RESET_ALL}"
            )
            self.log(
                f"{Fore.CYAN+Style.BRIGHT}     Block   :{Style.RESET_ALL}"
                f"{Fore.WHITE+Style.BRIGHT} {block_number} {Style.RESET_ALL}"
            )
            self.log(
                f"{Fore.CYAN+Style.BRIGHT}     Tx Hash :{Style.RESET_ALL}"
                f"{Fore.WHITE+Style.BRIGHT} {tx_hash} {Style.RESET_ALL}"
            )
            self.log(
                f"{Fore.CYAN+Style.BRIGHT}     Explorer:{Style.RESET_ALL}"
                f"{Fore.WHITE+Style.BRIGHT} {explorer} {Style.RESET_ALL}"
            )
        else:
            self.log(
                f"{Fore.CYAN+Style.BRIGHT}     Status  :{Style.RESET_ALL}"
                f"{Fore.RED+Style.BRIGHT} Perform On-Chain Failed {Style.RESET_ALL}"
            )

    async def process_option_1(self, account: str, address: str, wrap_option: int, wrap_amount: float):
        if wrap_option == 1:
            self.log(f"{Fore.CYAN+Style.BRIGHT}Wrap      :{Style.RESET_ALL}                      ")

            balance = await self.get_token_balance(address, "XOS")
            self.log(
                f"{Fore.CYAN+Style.BRIGHT}     Balance :{Style.RESET_ALL}"
                f"{Fore.WHITE+Style.BRIGHT} {balance} XOS {Style.RESET_ALL}"
            )
            self.log(
                f"{Fore.CYAN+Style.BRIGHT}     Amount  :{Style.RESET_ALL}"
                f"{Fore.WHITE+Style.BRIGHT} {wrap_amount} XOS {Style.RESET_ALL}"
            )

            if not balance or balance <= wrap_amount:
                self.log(
                    f"{Fore.CYAN+Style.BRIGHT}     Status  :{Style.RESET_ALL}"
                    f"{Fore.YELLOW+Style.BRIGHT} Insufficient XOS Token Balance {Style.RESET_ALL}"
                )
                return
            
            await self.process_perform_wrap(account, address, wrap_amount)
        
        elif wrap_option == 2:
            self.log(f"{Fore.CYAN+Style.BRIGHT}Unwrap    :{Style.RESET_ALL}                      ")

            balance = await self.get_token_balance(address, self.WXOS_CONTRACT_ADDRESS)
            self.log(
                f"{Fore.CYAN+Style.BRIGHT}     Balance :{Style.RESET_ALL}"
                f"{Fore.WHITE+Style.BRIGHT} {balance} WXOS {Style.RESET_ALL}"
            )
            self.log(
                f"{Fore.CYAN+Style.BRIGHT}     Amount  :{Style.RESET_ALL}"
                f"{Fore.WHITE+Style.BRIGHT} {wrap_amount} WXOS {Style.RESET_ALL}"
            )

            if not balance or balance <= wrap_amount:
                self.log(
                    f"{Fore.CYAN+Style.BRIGHT}     Status  :{Style.RESET_ALL}"
                    f"{Fore.YELLOW+Style.BRIGHT} Insufficient WXOS Token Balance {Style.RESET_ALL}"
                )
                return
            
            await self.process_perform_unwrap(account, address, wrap_amount)

    async def process_option_2(self, account: str, address: str, swap_count: int, min_swap_amount: float, max_swap_amount: float):
        self.log(f"{Fore.CYAN+Style.BRIGHT}Swap      :{Style.RESET_ALL}                       ")

        for i in range(swap_count):
            self.log(
                f"{Fore.MAGENTA+Style.BRIGHT}   ● {Style.RESET_ALL}"
                f"{Fore.GREEN+Style.BRIGHT}Swap{Style.RESET_ALL}"
                f"{Fore.WHITE+Style.BRIGHT} {i+1} / {swap_count} {Style.RESET_ALL}                           "
            )

            from_contract_address, to_contract_address, from_token, to_token = self.generate_swap_option()

            self.log(
                f"{Fore.CYAN+Style.BRIGHT}     Type    :{Style.RESET_ALL}"
                f"{Fore.GREEN+Style.BRIGHT} {from_token} {Style.RESET_ALL}"
                f"{Fore.MAGENTA+Style.BRIGHT}-{Style.RESET_ALL}"
                f"{Fore.GREEN+Style.BRIGHT} {to_token} {Style.RESET_ALL}"
            )

            swap_amount = round(random.uniform(min_swap_amount, max_swap_amount), 6)

            balance = await self.get_token_balance(address, from_contract_address)
            self.log(
                f"{Fore.CYAN+Style.BRIGHT}     Balance :{Style.RESET_ALL}"
                f"{Fore.WHITE+Style.BRIGHT} {balance} {from_token} {Style.RESET_ALL}"
            )
            self.log(
                f"{Fore.CYAN+Style.BRIGHT}     Amount  :{Style.RESET_ALL}"
                f"{Fore.WHITE+Style.BRIGHT} {swap_amount} {from_token} {Style.RESET_ALL}"
            )

            if not balance or balance <= swap_amount:
                self.log(
                    f"{Fore.CYAN+Style.BRIGHT}     Status  :{Style.RESET_ALL}"
                    f"{Fore.YELLOW+Style.BRIGHT} Insufficient {from_token} Token Balance {Style.RESET_ALL}"
                )
                continue

            await self.process_perform_swap(account, address, from_contract_address, to_contract_address, from_token, to_token, swap_amount)
            await self.print_timer(15, 20)

    async def process_accounts(self, account: str, address: str, option: int, wrap_option: int, wrap_amount: float, swap_count: int, min_swap_amount: float, max_swap_amount: float, use_proxy: bool, rotate_proxy: bool):
        is_valid = await self.process_check_connection(address, use_proxy, rotate_proxy)
        if is_valid:

            if option == 1:
                wrap_type = "Wrap XOS to WXOS" if wrap_option == 1 else "Unwrap WXOS to XOS"
                self.log(
                    f"{Fore.CYAN+Style.BRIGHT}Option    :{Style.RESET_ALL}"
                    f"{Fore.BLUE+Style.BRIGHT} {wrap_type} {Style.RESET_ALL}"
                )
                
                await self.process_option_1(account, address, wrap_option, wrap_amount)

            elif option == 2:
                self.log(
                    f"{Fore.CYAN+Style.BRIGHT}Option    :{Style.RESET_ALL}"
                    f"{Fore.BLUE+Style.BRIGHT} Swap  {Style.RESET_ALL}"
                )

                await self.process_option_2(account, address, swap_count, min_swap_amount, max_swap_amount)

            else:
                self.log(
                    f"{Fore.CYAN+Style.BRIGHT}Option    :{Style.RESET_ALL}"
                    f"{Fore.BLUE+Style.BRIGHT} Run All Features {Style.RESET_ALL}"
                )

                await self.process_option_1(account, address, wrap_option, wrap_amount)
                await asyncio.sleep(5)

                await self.process_option_2(account, address, swap_count, min_swap_amount, max_swap_amount)
                await asyncio.sleep(5)

    async def main(self):
        try:
            with open('accounts.txt', 'r') as file:
                accounts = [line.strip() for line in file if line.strip()]
            
            option, wrap_option, wrap_amount, swap_count, min_swap_amount, max_swap_amount, use_proxy_choice, rotate_proxy = self.print_question()

            while True:
                use_proxy = False
                if use_proxy_choice in [1, 2]:
                    use_proxy = True

                self.clear_terminal()
                self.welcome()
                self.log(
                    f"{Fore.GREEN + Style.BRIGHT}Account's Total: {Style.RESET_ALL}"
                    f"{Fore.WHITE + Style.BRIGHT}{len(accounts)}{Style.RESET_ALL}"
                )

                if use_proxy:
                    await self.load_proxies(use_proxy_choice)
                
                separator = "=" * 25
                for account in accounts:
                    if account:
                        address = self.generate_address(account)
                        self.log(
                            f"{Fore.CYAN + Style.BRIGHT}{separator}[{Style.RESET_ALL}"
                            f"{Fore.WHITE + Style.BRIGHT} {self.mask_account(address)} {Style.RESET_ALL}"
                            f"{Fore.CYAN + Style.BRIGHT}]{separator}{Style.RESET_ALL}"
                        )

                        if address:
                            await self.process_accounts(account, address, option, wrap_option, wrap_amount, swap_count, min_swap_amount, max_swap_amount, use_proxy, rotate_proxy)
                            await asyncio.sleep(3)

                self.log(f"{Fore.CYAN + Style.BRIGHT}={Style.RESET_ALL}"*72)
                seconds = 24 * 60 * 60
                while seconds > 0:
                    formatted_time = self.format_seconds(seconds)
                    print(
                        f"{Fore.CYAN+Style.BRIGHT}[ Wait for{Style.RESET_ALL}"
                        f"{Fore.WHITE+Style.BRIGHT} {formatted_time} {Style.RESET_ALL}"
                        f"{Fore.CYAN+Style.BRIGHT}... ]{Style.RESET_ALL}"
                        f"{Fore.WHITE+Style.BRIGHT} | {Style.RESET_ALL}"
                        f"{Fore.BLUE+Style.BRIGHT}All Accounts Have Been Processed.{Style.RESET_ALL}",
                        end="\r"
                    )
                    await asyncio.sleep(1)
                    seconds -= 1

        except FileNotFoundError:
            self.log(f"{Fore.RED}File 'accounts.txt' Not Found.{Style.RESET_ALL}")
            return
        except Exception as e:
            self.log(f"{Fore.RED+Style.BRIGHT}Error: {e}{Style.RESET_ALL}")
            raise e

if __name__ == "__main__":
    try:
        bot = XosTestnet()
        asyncio.run(bot.main())
    except KeyboardInterrupt:
        print(
            f"{Fore.CYAN + Style.BRIGHT}[ {datetime.now().astimezone(wib).strftime('%x %X %Z')} ]{Style.RESET_ALL}"
            f"{Fore.WHITE + Style.BRIGHT} | {Style.RESET_ALL}"
            f"{Fore.RED + Style.BRIGHT}[ EXIT ] XOS Testnet - BOT{Style.RESET_ALL}                                       "                              
        )