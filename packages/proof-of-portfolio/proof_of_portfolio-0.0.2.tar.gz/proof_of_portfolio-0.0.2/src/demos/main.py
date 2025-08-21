import json
import subprocess
import toml
import re
import os
import time

# Constants for the circuit
MAX_CHECKPOINTS = 200
MAX_SIGNALS = 256
MERKLE_DEPTH = 8
ARRAY_SIZE = 256
SCALING_FACTOR = 10**9
MAX_DAYS = 120


def run_command(command, cwd):
    """Executes a command in a given directory and returns the output."""
    result = subprocess.run(command, capture_output=True, text=True, cwd=cwd)
    print("--- nargo stdout ---")
    print(result.stdout)
    print("--- nargo stderr ---")
    print(result.stderr)
    print("--------------------")
    if result.returncode != 0:
        print("Error:")
        print(result.stdout)
        print(result.stderr)
        raise RuntimeError(
            f"Command {' '.join(command)} failed with exit code {result.returncode}"
        )
    return result.stdout


def parse_nargo_struct_output(output):
    """
    Parses the raw output of a nargo execute command that returns a struct.
    It finds all the Field values in the output, which is simpler and more robust
    than trying to parse the nested struct/vec syntax. Unfortunate that there is no clean JSON output.
    """
    return re.findall(r"Field\(([-0-9]+)\)", output)


def field_to_toml_value(f):
    """Converts a negative integer field to a proper field element string."""
    PRIME = (
        21888242871839275222246405745257275088548364400416034343698204186575808495617
    )
    if f < 0:
        return str(f + PRIME)
    return str(f)


def run_bb_prove_and_verify(circuit_dir, circuit_name="main"):
    """
    Runs barretenberg proving and verification.
    Returns proof generation time and verification status.
    """
    print(f"\n--- Running Barretenberg Proof Generation ---")

    try:
        subprocess.run(["bb", "--version"], capture_output=True, check=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        print(
            "Error: bb (Barretenberg) not found. Please install it using \n`curl -L https://raw.githubusercontent.com/AztecProtocol/aztec-packages/refs/heads/master/barretenberg/bbup/install | bash`.\n See here for more details: https://github.com/AztecProtocol/aztec-packages/blob/master/barretenberg/bbup/README.md#installation"
        )
        return None, False

    print("Compiling circuit...")
    compile_start = time.time()
    compile_result = subprocess.run(
        ["nargo", "compile"], cwd=circuit_dir, capture_output=True, text=True
    )
    compile_time = time.time() - compile_start

    if compile_result.returncode != 0:
        print(f"Circuit compilation failed:")
        print(compile_result.stdout)
        print(compile_result.stderr)
        return None, False

    print(f"Compilation completed in {compile_time:.3f}s")
    target_dir = os.path.join(circuit_dir, "target")
    json_files = [f for f in os.listdir(target_dir) if f.endswith(".json")]
    gz_files = [f for f in os.listdir(target_dir) if f.endswith(".gz")]

    if not json_files:
        print("Error: No compiled circuit (.json) found in target directory")
        return None, False
    if not gz_files:
        print("Error: No witness (.gz) found in target directory")
        return None, False

    circuit_json = json_files[0]
    witness_gz = gz_files[0]

    print(f"Using compiled circuit: {circuit_json}")
    print(f"Using witness file: {witness_gz}")

    print("Generating proof...")
    prove_start = time.time()
    prove_result = subprocess.run(
        [
            "bb",
            "prove",
            "-b",
            f"target/{circuit_json}",
            "-w",
            f"target/{witness_gz}",
            "-o",
            "proof",
        ],
        cwd=circuit_dir,
        capture_output=True,
        text=True,
    )
    prove_time = time.time() - prove_start

    if prove_result.returncode != 0:
        print(f"Proof generation failed:")
        print(prove_result.stdout)
        print(prove_result.stderr)
        return None, False

    print(f"Proof generation completed in {prove_time:.3f}s")

    print("Writing vk...")
    vk_dir = os.path.join(circuit_dir, "verification_key")
    os.makedirs(vk_dir, exist_ok=True)
    vk_path = os.path.join(vk_dir, "vk")

    vk_start = time.time()
    vk_result = subprocess.run(
        ["bb", "write_vk", "-b", f"target/{circuit_json}", "-o", vk_dir],
        cwd=circuit_dir,
        capture_output=True,
        text=True,
    )
    vk_time = time.time() - vk_start

    if vk_result.returncode != 0:
        print(f"Verification key generation failed:")
        print(vk_result.stdout)
        print(vk_result.stderr)
        return prove_time, False

    print(f"Verification key written in {vk_time:.3f}s")

    print("Verifying proof...")
    verify_start = time.time()
    verify_result = subprocess.run(
        [
            "bb",
            "verify",
            "-p",
            "proof/proof",
            "-k",
            vk_path,
            "-i",
            "proof/public_inputs",
        ],
        cwd=circuit_dir,
        capture_output=True,
        text=True,
    )
    verify_time = time.time() - verify_start

    verification_success = verify_result.returncode == 0

    if verification_success:
        print(f"✅ Proof verification PASSED in {verify_time:.3f}s")
    else:
        print(f"❌ Proof verification FAILED in {verify_time:.3f}s")
        print(verify_result.stdout)
        print(verify_result.stderr)

    print(f"Total circuit operations time: {prove_time + vk_time + verify_time:.3f}s")

    return prove_time, verification_success


def main(args):
    """Main function to run the demo."""
    hotkey = args.hotkey
    print("Loading data from validator_checkpoint.json...")
    with open("validator_checkpoint.json", "r") as f:
        data = json.load(f)

    if hotkey:
        if hotkey not in data["perf_ledgers"]:
            print(f"Error: Hotkey '{hotkey}' not found in validator checkpoint data.")
            print(f"Available hotkeys: {list(data['perf_ledgers'].keys())}")
            return
        miner_hotkey = hotkey
        print(f"Using specified hotkey: {miner_hotkey}")
    else:
        miner_hotkey = list(data["perf_ledgers"].keys())[0]
        print(f"No hotkey specified, using first available: {miner_hotkey}")

    perf_ledger = data["perf_ledgers"][miner_hotkey]
    positions = data["positions"][miner_hotkey]["positions"]
    print("Preparing circuit inputs...")

    cps = perf_ledger["cps"]
    checkpoint_count = len(cps)
    if checkpoint_count > MAX_CHECKPOINTS:
        print(
            f"Warning: Miner has {checkpoint_count} checkpoints, but circuit only supports {MAX_CHECKPOINTS}. Truncating."
        )
        cps = cps[:MAX_CHECKPOINTS]
        checkpoint_count = MAX_CHECKPOINTS

    gains = [int(c["gain"] * SCALING_FACTOR) for c in cps]
    losses = [int(c["loss"] * SCALING_FACTOR) for c in cps]
    last_update_times = [c["last_update_ms"] for c in cps]
    accum_times = [c["accum_ms"] for c in cps]
    target_duration = perf_ledger["target_cp_duration_ms"]

    # Pad
    gains += [0] * (MAX_CHECKPOINTS - len(gains))
    losses += [0] * (MAX_CHECKPOINTS - len(losses))
    last_update_times += [0] * (MAX_CHECKPOINTS - len(last_update_times))
    accum_times += [0] * (MAX_CHECKPOINTS - len(accum_times))

    all_orders = []
    for pos in positions:
        all_orders.extend(pos["orders"])

    signals_count = len(all_orders)
    if signals_count > MAX_SIGNALS:
        print(
            f"Warning: Miner has {signals_count} signals, but circuit only supports {MAX_SIGNALS}. Truncating."
        )
        all_orders = all_orders[:MAX_SIGNALS]
        signals_count = MAX_SIGNALS

    trade_pair_map = {}
    trade_pair_counter = 0

    signals = []
    for order in all_orders:
        trade_pair_str = order.get("trade_pair", ["UNKNOWN"])[0]
        if trade_pair_str not in trade_pair_map:
            trade_pair_map[trade_pair_str] = trade_pair_counter
            trade_pair_counter += 1

        order_type_str = order["order_type"]
        order_type_map = {"SHORT": -1, "LONG": 1, "FLAT": 0}
        price = int(order.get("price", 0) * SCALING_FACTOR)
        order_uuid = order.get("order_uuid", "0")
        bid = int(order.get("bid", 0) * SCALING_FACTOR)
        ask = int(order.get("ask", 0) * SCALING_FACTOR)
        processed_ms = order.get("processed_ms", 0)

        signals.append(
            {
                "trade_pair": str(trade_pair_map[trade_pair_str]),
                "order_type": str(order_type_map.get(order_type_str, 0)),
                "leverage": str(int(abs(order.get("leverage", 0)) * SCALING_FACTOR)),
                "price": str(price),
                "processed_ms": str(processed_ms),
                "order_uuid": f"0x{order_uuid.replace('-', '')}",
                "bid": str(bid),
                "ask": str(ask),
            }
        )

    # Pad signals too
    signals += [
        {
            "trade_pair": "0",
            "order_type": "0",
            "leverage": "0",
            "price": "0",
            "processed_ms": "0",
            "order_uuid": "0x0",
            "bid": "0",
            "ask": "0",
        }
    ] * (MAX_SIGNALS - len(signals))

    print(f"Prepared {checkpoint_count} checkpoints and {signals_count} signals.")

    print("Running tree_generator circuit...")
    tree_generator_dir = os.path.abspath("tree_generator")

    tree_prover_input = {"signals": signals, "actual_len": str(signals_count)}
    with open(os.path.join(tree_generator_dir, "Prover.toml"), "w") as f:
        toml.dump(tree_prover_input, f)

    output = run_command(["nargo", "execute", "--silence-warnings"], tree_generator_dir)

    fields = parse_nargo_struct_output(output)
    num_leaves = MAX_SIGNALS
    num_path_elements = MAX_SIGNALS * MERKLE_DEPTH
    num_path_indices = MAX_SIGNALS * MERKLE_DEPTH

    path_elements_flat = fields[num_leaves : num_leaves + num_path_elements]
    path_indices_flat = fields[
        num_leaves
        + num_path_elements : num_leaves
        + num_path_elements
        + num_path_indices
    ]
    signals_merkle_root = fields[-1]

    path_elements = [
        path_elements_flat[i : i + MERKLE_DEPTH]
        for i in range(0, len(path_elements_flat), MERKLE_DEPTH)
    ]
    path_indices = [
        path_indices_flat[i : i + MERKLE_DEPTH]
        for i in range(0, len(path_indices_flat), MERKLE_DEPTH)
    ]

    print(f"Generated signals Merkle root: {signals_merkle_root}")
    print(f"Signals Merkle root (hex): {hex(int(signals_merkle_root)).zfill(64)}")

    # This one is similar to tree gen but is the validator's contribution to the circuit (cps)
    print("Running returns_generator circuit...")
    returns_generator_dir = os.path.abspath("returns_generator")

    returns_prover_input = {
        "gains": [str(g) for g in gains],
        "losses": [str(l) for l in losses],
        "last_update_times": [str(t) for t in last_update_times],
        "accum_times": [str(a) for a in accum_times],
        "checkpoint_count": str(checkpoint_count),
        "target_duration": str(target_duration),
    }

    with open(os.path.join(returns_generator_dir, "Prover.toml"), "w") as f:
        toml.dump(returns_prover_input, f)

    output = run_command(
        ["nargo", "execute", "--silence-warnings"], returns_generator_dir
    )

    fields = parse_nargo_struct_output(output)
    num_log_returns = MAX_DAYS
    returns_merkle_root = fields[num_log_returns]
    valid_days = fields[-1]

    print(f"Generated returns Merkle root: {returns_merkle_root}")
    print(f"Returns Merkle root (hex): {hex(int(returns_merkle_root)).zfill(64)}")
    print(f"Number of valid daily returns: {valid_days}")

    print("Running main proof of portfolio circuit...")
    main_circuit_dir = os.path.abspath("circuits")

    # Finally, LFG
    main_prover_input = {
        "gains": [str(g) for g in gains],
        "losses": [str(l) for l in losses],
        "last_update_times": [str(t) for t in last_update_times],
        "accum_times": [str(a) for a in accum_times],
        "checkpoint_count": str(checkpoint_count),
        "target_duration": str(target_duration),
        "signals": signals,
        "signals_count": str(signals_count),
        "path_elements": [
            [field_to_toml_value(int(x)) for x in p] for p in path_elements
        ],
        "path_indices": path_indices,  # These are small, so no conversion needed
        "signals_merkle_root": field_to_toml_value(int(signals_merkle_root)),
        "returns_merkle_root": field_to_toml_value(int(returns_merkle_root)),
    }

    with open(os.path.join(main_circuit_dir, "Prover.toml"), "w") as f:
        toml.dump(main_prover_input, f)

    print("Executing main circuit to generate witness...")
    witness_start = time.time()
    output = run_command(["nargo", "execute", "--silence-warnings"], main_circuit_dir)
    witness_time = time.time() - witness_start
    print(f"Witness generation completed in {witness_time:.3f}s")

    fields = re.findall(r"Field\(([-0-9]+)\)", output)
    sharpe_raw = fields[0]
    drawdown_raw = fields[1]

    def field_to_signed_int(field_str):
        val = int(field_str)
        # Convert from field element to signed integer
        PRIME = 21888242871839275222246405745257275088548364400416034343698204186575808495617
        if val > PRIME // 2:
            val = val - PRIME
        return val

    sharpe_ratio_raw = field_to_signed_int(sharpe_raw)
    max_drawdown_raw = field_to_signed_int(drawdown_raw)

    sharpe_ratio_scaled = sharpe_ratio_raw / SCALING_FACTOR
    max_drawdown_scaled = max_drawdown_raw / SCALING_FACTOR

    prove_time, verification_success = run_bb_prove_and_verify(main_circuit_dir)

    print("\n--- Proof Generation Complete ---")
    print("\n=== MERKLE ROOTS ===")
    print(f"Signals Merkle Root: {signals_merkle_root}")
    print(f"Returns Merkle Root: {returns_merkle_root}")

    print("\n=== PORTFOLIO METRICS ===")
    print(f"Sharpe Ratio (raw): {sharpe_ratio_raw}")
    print(f"Sharpe Ratio (scaled): {sharpe_ratio_scaled:.9f}")
    print(f"Max Drawdown (raw): {max_drawdown_raw}")
    print(
        f"Max Drawdown (scaled): {max_drawdown_scaled:.9f} ({max_drawdown_scaled * 100:.6f}%)"
    )

    print("\n=== DATA SUMMARY ===")
    print(f"Checkpoints processed: {checkpoint_count}")
    print(f"Trading signals processed: {signals_count}")
    print(f"Valid daily returns: {valid_days}")

    print("\n=== PROOF GENERATION RESULTS ===")
    print(f"Witness generation time: {witness_time:.3f}s")
    if prove_time is not None:
        print(f"Proof generation time: {prove_time:.3f}s")
        print(
            f"Proof verification: {'✅ PASSED' if verification_success else '❌ FAILED'}"
        )
    else:
        print("Unable to prove or verify due to an error.")

    # Return structured results for programmatic access
    return {
        "merkle_roots": {
            "signals": signals_merkle_root,
            "returns": returns_merkle_root
        },
        "portfolio_metrics": {
            "sharpe_ratio_raw": sharpe_ratio_raw,
            "sharpe_ratio_scaled": sharpe_ratio_scaled,
            "max_drawdown_raw": max_drawdown_raw,
            "max_drawdown_scaled": max_drawdown_scaled,
            "max_drawdown_percentage": max_drawdown_scaled * 100
        },
        "data_summary": {
            "checkpoints_processed": checkpoint_count,
            "signals_processed": signals_count,
            "valid_daily_returns": int(valid_days)
        },
        "proof_results": {
            "witness_generation_time": witness_time,
            "proof_generation_time": prove_time,
            "verification_success": verification_success,
            "proof_generated": prove_time is not None
        }
    }
