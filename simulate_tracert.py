import subprocess
import re
import sys

def find_ip(output):
    #finds the IP address based on hop_info provided
    hop_info = re.search(r"\[.*?\>", output)
    if hop_info is None:
        print("Destination not reached")        #some ip address can't be tracerouted - eventually leads to rows of "Request Timed Out" and no packets received back on using nping
        sys.exit()

    ip = hop_info.group(0)[1:]
    ip = ip[:-2]
    return ip

def get_rtt(output):
    #finds RTT times in output provided by ping
    rtt_values = re.findall(r"(\d+\.\d+)ms", output)
    rtt_values = [int(float(x)) for x in rtt_values]
    return rtt_values

def simulate_traceroute(target, max_hops):
    #main function that replicates tracert behaviour using nping
    #tagret = ip_address
    #max_hops = 30 by default
    print(f"Tracing route to {target} over a maximum of {max_hops} hops\n")
    for ttl in range(1, max_hops + 1):                                      #incrementing TTL to get routers in path
        command = ["nping", "-c 3","-H", "--icmp", "--ttl", str(ttl), target]
        try:
            result = subprocess.run(command, capture_output=True, text=True, timeout=10)
            if "Rcvd: 0" in result.stdout:  #no packets received back
                print(f"{ttl:<4}{'*':>6}   {'*':>6}   {'*':>6}      {'Request timed out':<23}")

            else: #al least one or all packets received back
                if "Rcvd: 1" in result.stdout:                                                              
                    rtt_values = get_rtt(result.stdout)
                    ip_addr = find_ip(result.stdout)

                    print(f"{ttl:<4}{rtt_values[0]:>6} ms{'*':>6}   {'*':>6}      {ip_addr:<23}")

                elif "Rcvd: 2" in result.stdout:                                                                  
                    rtt_values = get_rtt(result.stdout)  #fetches the min and max rtt
                    ip_addr = find_ip(result.stdout)

                    print(f"{ttl:<4}{rtt_values[0]:>6} ms{rtt_values[1]:>6} ms{'*':>6}      {ip_addr:<23}")

                else:#all 3 packets received back( in some cases more than 3 received even if sent 3)                                                            
                    rtt_values = re.findall(r"(\d+\.\d+)ms", result.stdout)
                    rtt_values = [float(x) for x in rtt_values]
                    rtt_values[2] = rtt_values[2]*3 -(rtt_values[0] - rtt_values[1])  #calculating RTT for 3 rd packet usin max,min and avg rtt
                    rtt_values = [int(x) for x in rtt_values]

                    ip_addr = find_ip(result.stdout)

                    print(f"{ttl:<4}{rtt_values[0]:>6} ms{rtt_values[1]:>6} ms{rtt_values[2]:>6} ms   {ip_addr:<23}")

            if target in result.stdout: #destination reached!
                print("\nTrace complete")
                break

        except subprocess.TimeoutExpired:
            print(f"Timeout expired for TTL {ttl}")

        except Exception as e:
            print(f"An error occurred: {e}")
            break
    

if __name__ == "__main__":
    # target_ip = input("Enter the target host or IP address: ") # Replace with the target IP or hostname
    if len(sys.argv) != 2:
        print("Usage: python traceroute.py <target_ip>")
        sys.exit(1)
    
    target_ip = sys.argv[1]
    command = ["nping", "-c 1","-H", "--icmp", str(target_ip)]
    try:
        result = subprocess.run(command, capture_output=True, text=True, timeout=10)
        ip_addr = find_ip(result.stdout)
        max_hops = 30  # Set the maximum number of hops
        simulate_traceroute(ip_addr, max_hops)

    except subprocess.TimeoutExpired:
            print("Timeout expired ")   #output if gibberish destination,etc.

    except Exception as e:
            print(f"An error occurred: {e}")
