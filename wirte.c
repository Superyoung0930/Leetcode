/*28. 找出字符串中第一个匹配项的下标
给你两个字符串 haystack 和 needle ，请你在 haystack 字符串中找出 needle 字符串的第一个匹配项的下标（下标从 0 开始）。
如果 needle 不是 haystack 的一部分，则返回  -1 。*/
int strStr(char* haystack, char* needle) {
    int n = strlen(haystack), m = strlen(needle);
    for(int i = 0; i <= n - m; i++){
        if(haystack[i] == needle[0]){
            int flag = true;
            for(int j = 0; j < m; j++){
                if(haystack[i + j] != needle[j]){
                    flag = false;
                    break;
                }
            }
            if(flag == true){
                return i;
            }
        }
    }
    return -1;
}

/*11. 盛最多水的容器
给定一个长度为 n 的整数数组 height 。有 n 条垂线，第 i 条线的两个端点是 (i, 0) 和 (i, height[i]) 。
找出其中的两条线，使得它们与 x 轴共同构成的容器可以容纳最多的水。返回容器可以储存的最大水量。
说明：你不能倾斜容器。*/
#define MAX(a, b) ((a) > (b) ? (a) : (b))
#define MIN(a, b) ((a) < (b) ? (a) : (b))

int maxArea(int* height, int heightSize) {
    int left = 0, right = heightSize - 1;
    int ans = 0;
    while(left < right){
        int area = (right - left) * MIN(height[left], height[right]);
        ans = MAX(area, ans);
        height[left] < height[right] ? (left++) : (right--);
    }
    return ans;
}

/*283. 移动零
给定一个数组 nums，编写一个函数将所有 0 移动到数组的末尾，同时保持非零元素的相对顺序。
请注意 ，必须在不复制数组的情况下原地对数组进行操作。*/
void moveZeroes(int* nums, int numsSize) {
    int left = 0, right = 0;
    while(right < numsSize){
        if(nums[right] != 0){
            int tmp = nums[right];
            nums[right] = nums[left];
            nums[left] = tmp;
            left++;
        }
        right++;
    }
}

/*56. 合并区间
以数组 intervals 表示若干个区间的集合，其中单个区间为 intervals[i] = [starti, endi] 。
请你合并所有重叠的区间，并返回 一个不重叠的区间数组，该数组需恰好覆盖输入中的所有区间 。*/
/**
 * Return an array of arrays of size *returnSize.
 * The sizes of the arrays are returned as *returnColumnSizes array.
 * Note: Both returned array and *columnSizes array must be malloced, assume caller calls free().
 */
int** merge(int** intervals, int intervalsSize, int* intervalsColSize, int* returnSize, int** returnColumnSizes) {
    
}

/*206. 反转链表
给你单链表的头节点 head ，请你反转链表，并返回反转后的链表。*/
/**
 * Definition for singly-linked list.
 * struct ListNode {
 *     int val;
 *     struct ListNode *next;
 * };
 */
struct ListNode* reverseList(struct ListNode* head) {
    struct ListNode* curr = head;
    struct ListNode* prev = NULL;
    while(curr){
        struct ListNode* next = curr->next;
        curr->next = prev;
        prev = curr;
        curr = next;
    }
    return prev;
}


/*141. 环形链表
给你一个链表的头节点 head ，判断链表中是否有环。如果链表中有某个节点，可以通过连续跟踪 next 指针再次到达，则链表中存在环。 
为了表示给定链表中的环，评测系统内部使用整数 pos 来表示链表尾连接到链表中的位置（索引从 0 开始）。
注意：pos 不作为参数进行传递 。仅仅是为了标识链表的实际情况。如果链表中存在环 ，则返回 true 。 否则，返回 false 。*/
/**
 * Definition for singly-linked list.
 * struct ListNode {
 *     int val;
 *     struct ListNode *next;
 * };
 */
bool hasCycle(struct ListNode *head) {
    if(head == NULL || head->next == NULL){
        return false;
    }
    struct ListNode* slow = head;
    struct ListNode* fast = head->next;
    while(slow != fast){
        if(fast == NULL || fast-> next == NULL){
            return false;
        }
        slow = slow->next;
        fast = fast->next->next;
    }
    return true;
}

/*
21. 合并两个有序链表
将两个升序链表合并为一个新的升序链表并返回。新链表是通过拼接给定的两个链表的所有节点组成的。*/
/**
 * Definition for singly-linked list.
 * struct ListNode {
 *     int val;
 *     struct ListNode *next;
 * };
 */
struct ListNode* mergeTwoLists(struct ListNode* list1, struct ListNode* list2) {
    struct ListNode dummy = {};
    struct ListNode* cur = &dummy;
    while(list1 && list2){
        if(list1->val < list2->val){
            cur->next = list1;
            list1 = list1->next;
        }else{
            cur->next = list2;
            list2 = list2->next;
        }
        cur = cur->next;
    }
    cur->next = list1 ? list1 : list2;

    return dummy.next;
}

/*83. 删除排序链表中的重复元素
给定一个已排序的链表的头head，删除所有重复的元素，使每个元素只出现一次 。返回已排序的链表 。*/
/**
 * Definition for singly-linked list.
 * struct ListNode {
 *     int val;
 *     struct ListNode *next;
 * };
 */
struct ListNode* deleteDuplicates(struct ListNode* head) {
    if(head == NULL){
        return head;
    }
    struct ListNode* cur = head;
    while(cur && cur->next){
        if(cur->val == cur->next->val){
            cur->next = cur->next->next;
        }else{
            cur = cur->next;
        }
    }
    return head;
}

/*225. 用队列实现栈
请你仅使用两个队列实现一个后入先出（LIFO）的栈，并支持普通栈的全部四种操作（push、top、pop 和 empty）。
实现 MyStack 类：
void push(int x) 将元素 x 压入栈顶。
int pop() 移除并返回栈顶元素。
int top() 返回栈顶元素。
boolean empty() 如果栈是空的，返回 true ；否则，返回 false 。
注意：
你只能使用队列的标准操作 —— 也就是push to back、peek/pop from front、size和is empty这些操作。
你所使用的语言也许不支持队列。 你可以使用 list （列表）或者 deque（双端队列）来模拟一个队列 , 只要是标准的队列操作即可。*/
#define LEN 20
typedef struct queue{
    int* data;
    int head;
    int rear;
    int size;
} Queue;

typedef struct {
    Queue *queue1, *queue2;
} MyStack;

Queue* initQueue(int k){
    Queue* obj = (Queue *)malloc(k * sizeof(Queue));
    obj->data = (int *)malloc(k * sizeof(int));
    obj->head = -1;
    obj->rear = -1;
    obj->size = k;
    return obj;
}

Queue* enQueue(Queue* obj, int e){
    if(obj->head == obj->rear){
        head = 0;
    }
    obj->rear = (obj->rear+1) % (obj->size);
    obj->data[rear] = e;
    return obj;
}

int deQueue(Queue* obj){
    if(obj->head == obj->rear){
        return -1;
    }
    
}

MyStack* myStackCreate(MyStack* obj, int x){
    
}

void myStackPush(MyStack* obj, int x){
    
}

int myStackPop(MyStack* obj)
{
    
}

int myStackTop(MyStack* obj) {
    
}

bool myStackEmpty(MyStack* obj) {
    
}

void myStackFree(MyStack* obj) {
    
}




typedef struct {
    
} MyStack;


MyStack* myStackCreate() {
    
}

void myStackPush(MyStack* obj, int x) {
    
}

int myStackPop(MyStack* obj) {
    
}

int myStackTop(MyStack* obj) {
    
}

bool myStackEmpty(MyStack* obj) {
    
}

void myStackFree(MyStack* obj) {
    
}

/**
 * Your MyStack struct will be instantiated and called as such:
 * MyStack* obj = myStackCreate();
 * myStackPush(obj, x);
 
 * int param_2 = myStackPop(obj);
 
 * int param_3 = myStackTop(obj);
 
 * bool param_4 = myStackEmpty(obj);
 
 * myStackFree(obj);
*/

/*232. 用栈实现队列
请你仅使用两个栈实现先入先出队列。队列应当支持一般队列支持的所有操作（push、pop、peek、empty）：
实现 MyQueue 类：
void push(int x) 将元素 x 推到队列的末尾
int pop() 从队列的开头移除并返回元素
int peek() 返回队列开头的元素
boolean empty() 如果队列为空，返回 true ；否则，返回 false
说明：你只能使用标准的栈操作——也就是只有 push to top, peek/pop from top, size, 和 is empty 操作是合法的。
你所使用的语言也许不支持栈。你可以使用 list 或者 deque（双端队列）来模拟一个栈，只要是标准的栈操作即可。*/

typedef struct {
    
} MyQueue;


MyQueue* myQueueCreate() {
    
}

void myQueuePush(MyQueue* obj, int x) {
    
}

int myQueuePop(MyQueue* obj) {
    
}

int myQueuePeek(MyQueue* obj) {
    
}

bool myQueueEmpty(MyQueue* obj) {
    
}

void myQueueFree(MyQueue* obj) {
    
}

/**
 * Your MyQueue struct will be instantiated and called as such:
 * MyQueue* obj = myQueueCreate();
 * myQueuePush(obj, x);
 
 * int param_2 = myQueuePop(obj);
 
 * int param_3 = myQueuePeek(obj);
 
 * bool param_4 = myQueueEmpty(obj);
 
 * myQueueFree(obj);
*/