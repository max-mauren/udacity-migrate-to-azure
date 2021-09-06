import logging
import psycopg2
import azure.functions as func
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from datetime import datetime

def main(msg: func.ServiceBusMessage):
    logging.info('Python ServiceBus queue trigger processed message: %s',
                 msg.get_body().decode('utf-8'))
    try:
        id = msg.get_body().decode('utf-8')
        logging.info('id: %s',id)

        if id:
            with psycopg2.connect("host=techconfdb.postgres.database.azure.com dbname=postgres user=tech_admin@techconfdb password=r74P@7Zg$76hV$9xg*f") as conn:
                with conn.cursor() as cur:
                    cur.execute("SELECT subject, message FROM public.notification WHERE id= %s;",(id,))

                    notifcation = cur.fetchone()
                    subject = notifcation[0]
                    message = notifcation[1]

                    # cur.close()
                    count = 0

                    sendgridapikey = ""

                    cur.execute("SELECT first_name, email FROM public.attendee")
                    for attendee in cur:
                        #send emails for each attendee
                        first_name=attendee[0]
                        email=attendee[1]

                        # if not sendgridapikey:
                        #     message = Mail(
                        #         from_email="max_mauren@hotmail.com",
                        #         to_emails=email,
                        #         subject=subject,
                        #         plain_text_content=message)

                        #     sg = SendGridAPIClient(sendgridapikey)
                        #     sg.send(message)

                        # count each one sent
                        count = count + 1

                    # update notification status
                    # statusmsg = str.join("Updated",str(count)," attendees")
                    completed_date = datetime.utcnow()
                    status = 'Notified {} attendees'.format(count)
                    
                    #params = [(status), ("completed_date":completed_date), ("id":id)]

                    #params = [Json({'status':status}, {'completed_date':completed_date}, {'id':id})]
                    params = (status,completed_date,id)
                    sql = """UPDATE public.notification SET status= %s, completed_date=%s WHERE id=%s"""
                    cur.execute(sql,params)
                    conn.commit()
             
    except Exception as e:
        logging.error("Error: %s", e)
