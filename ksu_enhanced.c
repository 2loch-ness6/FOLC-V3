#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <string.h>
#include <sys/types.h>
#include <sys/prctl.h>
#include <linux/capability.h>
#include <sys/syscall.h>

// Direct syscall to avoid libcap dependency
int capset(cap_user_header_t header, cap_user_data_t data) {
    return syscall(SYS_capset, header, data);
}

int main(int argc, char *argv[]) {
    // 1. Set Keep Caps (Vital for transition)
    if (prctl(PR_SET_KEEPCAPS, 1, 0, 0, 0) != 0) {
        perror("prctl(KEEPCAPS)");
        // Continue anyway, might work if started as root
    }

    // 2. Switch to Root
    if (setgid(0) != 0) { perror("setgid"); return 1; }
    if (setuid(0) != 0) { perror("setuid"); return 1; }

    // 3. Craft Full Capabilities (0x3fffffffff for this kernel)
    struct __user_cap_header_struct head;
    struct __user_cap_data_struct data[2];

    head.version = _LINUX_CAPABILITY_VERSION_3;
    head.pid = 0;

    // Fill with all ones (Full Power)
    data[0].effective = data[0].permitted = data[0].inheritable = 0xffffffff;
    data[1].effective = data[1].permitted = data[1].inheritable = 0x0000003f; // Adjust high bits as needed

    if (capset(&head, data) != 0) {
        perror("capset");
        // Continue, we might already have them
    }

    // 4. Execute Shell or Command
    if (argc > 1) {
        // Handle -c flag for compatibility with standard 'su'
        if (argc >= 3 && strcmp(argv[1], "-c") == 0) {
            char *args[] = {"/bin/sh", "-c", argv[2], NULL};
            execv("/bin/sh", args);
        } else {
            execvp(argv[1], &argv[1]);
        }
    } else {
        char *args[] = {"/bin/sh", NULL};
        execv("/bin/sh", args);
    }
    
    perror("exec");
    return 1;
}
