#include <stdio.h>
#include <sys/prctl.h>
#include <linux/capability.h>
#include <sys/types.h>
#include <unistd.h>
#include <errno.h>

int main() {
    printf("Initial UID: %d\n", getuid());
    if (prctl(PR_CAPBSET_DROP, CAP_SYS_ADMIN, 0, 0, 0) == 0) {
        printf("Dropped CAP_SYS_ADMIN (should NOT happen if hooked)\n");
    } else {
        perror("prctl DROP failed (GOOD if hooked)");
    }
    return 0;
}
